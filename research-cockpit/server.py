#!/usr/bin/env python3
"""Local Wave web-widget backend for research session control state."""

from __future__ import annotations

import json
import os
import shlex
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import RLock
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlparse


HOST = "127.0.0.1"
PORT = int(os.environ.get("RESEARCH_COCKPIT_PORT", "8792"))
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
CONFIG_PATH = ROOT / "config.json"
CONFIG_TEMPLATE_PATH = ROOT / "config.template.json"
DEFAULT_STATE_PATH = ROOT / "state" / "session.json"
STATE_LOCK = RLock()


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def load_config() -> dict[str, Any]:
    source = CONFIG_PATH if CONFIG_PATH.exists() else CONFIG_TEMPLATE_PATH
    if source.exists():
        return json.loads(source.read_text())
    return {
        "title": "Research Cockpit",
        "refreshInterval": 5,
        "profiles": [],
        "workflows": [],
        "sourceTypes": [],
        "copyableCommands": [],
        "state": {"file": "state/session.json"},
    }


def state_path() -> Path:
    configured = load_config().get("state", {}).get("file", "state/session.json")
    path = Path(str(configured))
    if path.is_absolute():
        return DEFAULT_STATE_PATH
    resolved = (ROOT / path).resolve()
    if ROOT.resolve() not in resolved.parents and resolved != ROOT.resolve():
        return DEFAULT_STATE_PATH
    return resolved


def default_state() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
        "session": {
            "title": "Untitled research session",
            "question": "",
            "scope": "",
            "expectedOutput": "",
            "phase": "brief",
            "status": "active",
        },
        "sources": [],
        "workerQueue": [],
        "notes": [],
        "claims": [],
        "openQuestions": [],
    }


def read_state() -> dict[str, Any]:
    with STATE_LOCK:
        path = state_path()
        if not path.exists():
            state = default_state()
            write_state(state)
            return state
        return json.loads(path.read_text())


def write_state(state: dict[str, Any]) -> dict[str, Any]:
    with STATE_LOCK:
        path = state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        state["updatedAt"] = now_iso()
        temp_path = path.with_suffix(path.suffix + ".tmp")
        temp_path.write_text(json.dumps(state, indent=2) + "\n")
        temp_path.replace(path)
        return state


def merge_state(current: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    for key, value in patch.items():
        if key in {"schemaVersion", "createdAt", "updatedAt"}:
            continue
        if isinstance(value, dict) and isinstance(current.get(key), dict):
            current[key].update(value)
        elif key in {"session", "sources", "workerQueue", "notes", "claims", "openQuestions"}:
            current[key] = value
    return current


def validate_source_url(url: str) -> str | None:
    value = str(url).strip()
    if not value:
        return "URL is empty."
    if "<" in value or ">" in value:
        return "URL still contains a placeholder."
    if any(char in value for char in "\r\n\t"):
        return "URL must not contain control characters."
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        return "URL must start with http:// or https://."
    if not parsed.netloc:
        return "URL is missing a host."
    if parsed.username or parsed.password:
        return "Do not put usernames, passwords, or tokens in source URLs."
    secret_words = {"api_key", "apikey", "auth", "key", "password", "secret", "token"}
    query_keys = {name.lower() for name in parse_qs(parsed.query, keep_blank_values=True)}
    if query_keys & secret_words:
        return "Do not store secret-bearing query parameters in source URLs."
    return None


def source_id(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower().replace(":", "-") or "source"
    stamp = str(int(time.time() * 1000))
    return f"src-{host}-{stamp}"


def source_view(source: dict[str, Any]) -> dict[str, Any]:
    item = dict(source)
    url = str(item.get("url", ""))
    item["openPath"] = f"/open/source/{quote(str(item.get('id', '')))}"
    item["waveWebOpenCommand"] = f"wsh web open {shlex.quote(url)}" if url else ""
    return item


def add_source(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    url = str(payload.get("url", "")).strip()
    error = validate_source_url(url)
    if error:
        return 400, {"ok": False, "error": error}

    state = read_state()
    source = {
        "id": source_id(url),
        "url": url,
        "title": str(payload.get("title", "")).strip(),
        "type": str(payload.get("type", "source")).strip() or "source",
        "status": str(payload.get("status", "queued")).strip() or "queued",
        "notes": str(payload.get("notes", "")).strip(),
        "tags": payload.get("tags", []) if isinstance(payload.get("tags", []), list) else [],
        "createdAt": now_iso(),
    }
    state.setdefault("sources", []).append(source)
    write_state(state)
    return 201, {"ok": True, "source": source_view(source), "state": state}


def add_list_item(collection: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    state = read_state()
    item = dict(payload)
    item.setdefault("id", f"{collection}-{int(time.time() * 1000)}")
    item.setdefault("createdAt", now_iso())
    state.setdefault(collection, []).append(item)
    write_state(state)
    return 201, {"ok": True, "item": item, "state": state}


def json_bytes(payload: dict[str, Any], status: int = 200) -> tuple[int, bytes]:
    return status, json.dumps(payload, indent=2).encode("utf-8")


class Handler(SimpleHTTPRequestHandler):
    server_version = "ResearchCockpit/1.0"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_payload(self, status: int, data: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        code, data = json_bytes(payload, status)
        self.send_payload(code, data, "application/json")

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("Expected a JSON object.")
        return parsed

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            self.send_json(
                {
                    "ok": True,
                    "service": "research-cockpit",
                    "host": HOST,
                    "port": PORT,
                    "stateFile": str(state_path().relative_to(ROOT)),
                    "configFile": "config.json" if CONFIG_PATH.exists() else "config.template.json",
                }
            )
            return

        if parsed.path == "/api/config":
            config = load_config()
            self.send_json(
                {
                    "title": config.get("title", "Research Cockpit"),
                    "refreshInterval": config.get("refreshInterval", 5),
                    "profiles": config.get("profiles", []),
                    "workflows": config.get("workflows", []),
                    "sourceTypes": config.get("sourceTypes", []),
                    "copyableCommands": config.get("copyableCommands", []),
                }
            )
            return

        if parsed.path == "/api/state":
            self.send_json({"ok": True, "state": read_state()})
            return

        if parsed.path == "/api/sources":
            sources = [source_view(item) for item in read_state().get("sources", [])]
            self.send_json({"ok": True, "sources": sources})
            return

        if parsed.path.startswith("/open/source/"):
            source_key = unquote(parsed.path.removeprefix("/open/source/")).strip()
            match = next(
                (item for item in read_state().get("sources", []) if item.get("id") == source_key),
                None,
            )
            if not match:
                self.send_json({"ok": False, "error": "Unknown source."}, 404)
                return
            error = validate_source_url(str(match.get("url", "")))
            if error:
                self.send_json({"ok": False, "error": error}, 400)
                return
            self.send_response(302)
            self.send_header("Location", str(match["url"]))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return

        if parsed.path == "/":
            self.path = "/index.html"
            super().do_GET()
            return

        if parsed.path in {"/index.html", "/app.js", "/styles.css"}:
            super().do_GET()
            return

        self.send_json({"ok": False, "error": "Not found."}, 404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self.read_json()

            if parsed.path == "/api/validate-source":
                error = validate_source_url(str(payload.get("url", "")))
                self.send_json({"ok": error is None, "error": error})
                return

            if parsed.path == "/api/sources":
                status, response = add_source(payload)
                self.send_json(response, status)
                return

            if parsed.path == "/api/notes":
                status, response = add_list_item("notes", payload)
                self.send_json(response, status)
                return

            if parsed.path == "/api/claims":
                status, response = add_list_item("claims", payload)
                self.send_json(response, status)
                return

            if parsed.path == "/api/worker-queue":
                status, response = add_list_item("workerQueue", payload)
                self.send_json(response, status)
                return

            self.send_json({"ok": False, "error": "Unknown action."}, 404)
        except (json.JSONDecodeError, ValueError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, 400)
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, 500)

    def do_PATCH(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path != "/api/state":
                self.send_json({"ok": False, "error": "Not found."}, 404)
                return
            state = merge_state(read_state(), self.read_json())
            self.send_json({"ok": True, "state": write_state(state)})
        except (json.JSONDecodeError, ValueError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, 400)

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path != "/api/state":
                self.send_json({"ok": False, "error": "Not found."}, 404)
                return
            payload = self.read_json()
            payload.setdefault("schemaVersion", 1)
            payload.setdefault("createdAt", now_iso())
            self.send_json({"ok": True, "state": write_state(payload)})
        except (json.JSONDecodeError, ValueError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, 400)


def main() -> None:
    STATIC.mkdir(exist_ok=True)
    state_path().parent.mkdir(parents=True, exist_ok=True)
    if not state_path().exists():
        write_state(default_state())
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Research Cockpit listening on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping Research Cockpit")


if __name__ == "__main__":
    sys.exit(main())
