#!/usr/bin/env python3
"""Local Wave web-widget launcher for native n8n UIs."""

from __future__ import annotations

import json
import os
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlparse


HOST = "127.0.0.1"
PORT = int(os.environ.get("N8N_LAUNCHER_PORT", "8791"))
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
CONFIG_PATH = ROOT / "config.json"
CONFIG_TEMPLATE_PATH = ROOT / "config.template.json"


def load_config() -> dict[str, Any]:
    source = CONFIG_PATH if CONFIG_PATH.exists() else CONFIG_TEMPLATE_PATH
    if source.exists():
        return json.loads(source.read_text())
    return {
        "title": "n8n Launcher",
        "instances": [
            {
                "id": "local",
                "name": "Local n8n",
                "url": "http://127.0.0.1:5678",
                "kind": "local",
                "enabled": True,
                "description": "Default local/community n8n UI",
            }
        ],
    }


def normalize_instance(raw: dict[str, Any]) -> dict[str, Any]:
    instance_id = str(raw.get("id", "")).strip()
    name = str(raw.get("name", instance_id or "n8n")).strip()
    url = str(raw.get("url", "")).strip()
    kind = str(raw.get("kind", "remote")).strip() or "remote"
    enabled = bool(raw.get("enabled", True))
    description = str(raw.get("description", "")).strip()
    return {
        "id": instance_id,
        "name": name,
        "url": url,
        "kind": kind,
        "enabled": enabled,
        "description": description,
        "openPath": f"/open/{quote(instance_id)}" if instance_id else "",
        "error": validate_url(url) if enabled else None,
    }


def configured_instances() -> list[dict[str, Any]]:
    config = load_config()
    instances = config.get("instances", [])
    return [normalize_instance(item) for item in instances if isinstance(item, dict)]


def validate_url(url: str) -> str | None:
    if not url:
        return "URL is empty."
    if "<" in url or ">" in url:
        return "URL still contains a placeholder."
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return "URL must start with http:// or https://."
    if not parsed.netloc:
        return "URL is missing a host."
    if parsed.username or parsed.password:
        return "Do not put usernames, passwords, or tokens in n8n URLs."
    return None


def json_bytes(payload: dict[str, Any], status: int = 200) -> tuple[int, bytes]:
    return status, json.dumps(payload, indent=2).encode("utf-8")


class Handler(SimpleHTTPRequestHandler):
    server_version = "N8nLauncher/1.0"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

    def send_payload(self, status: int, data: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def redirect_to(self, target: str) -> None:
        self.send_response(302)
        self.send_header("Location", target)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        code, data = json_bytes(payload, status)
        self.send_payload(code, data, "application/json")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            self.send_json({"ok": True})
            return

        if parsed.path == "/api/config":
            config = load_config()
            self.send_json(
                {
                    "title": config.get("title", "n8n Launcher"),
                    "configFile": "config.json",
                    "instances": configured_instances(),
                }
            )
            return

        if parsed.path.startswith("/open/"):
            instance_id = unquote(parsed.path.removeprefix("/open/")).strip()
            match = next(
                (item for item in configured_instances() if item["id"] == instance_id),
                None,
            )
            if not match:
                self.send_json({"ok": False, "error": "Unknown n8n instance."}, 404)
                return
            if not match["enabled"]:
                self.send_json({"ok": False, "error": "This n8n instance is disabled."}, 403)
                return
            if match["error"]:
                self.send_json({"ok": False, "error": match["error"]}, 400)
                return
            self.redirect_to(match["url"])
            return

        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()


def main() -> None:
    STATIC.mkdir(exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"n8n Launcher listening on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping n8n Launcher")


if __name__ == "__main__":
    sys.exit(main())
