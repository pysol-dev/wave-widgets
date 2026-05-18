#!/usr/bin/env python3
"""Wave Terminal widget dashboard for local and remote model servers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


HOST = "127.0.0.1"
PORT = int(os.environ.get("MODEL_DASHBOARD_PORT", "8787"))
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
CONFIG_PATH = ROOT / "config.json"
DEFAULT_CONFIG_SAMPLE = ROOT / "config.template.json"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict[str, Any]:
    """Load config.json, falling back to the template with descriptive warnings."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)

    if DEFAULT_CONFIG_SAMPLE.exists():
        cfg = json.loads(DEFAULT_CONFIG_SAMPLE.read_text())
        for srv in cfg.get("servers", []):
            if srv.get("ssh_host") and srv["ssh_host"].startswith("<"):
                srv["_error"] = f"SSH host '{srv['ssh_host']}' not configured"
        return cfg

    return {"servers": [], "title": "Model Servers", "refreshInterval": 30}


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------

def run_text(args: list[str], timeout: int = 10) -> str:
    try:
        completed = subprocess.run(
            args,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"ERROR: {exc}"
    return completed.stdout or completed.stderr


def fetch_text(url: str, timeout: int = 5) -> str:
    """Fetch a URL via direct HTTP."""
    try:
        req = Request(url, headers={"User-Agent": "WaveModelDashboard/1.0"})
        with urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except (OSError, URLError) as exc:
        return f"ERROR: {exc}"


def fetch_via_ssh(ssh_host: str, url: str, timeout: int = 8) -> str:
    """Fetch a localhost URL on a remote host over SSH (Tailscale)."""
    return run_text(["ssh", "-o", "ConnectTimeout=5", ssh_host, "curl", "-s", url], timeout=timeout)


def fetch_safe(server: dict[str, Any], endpoint: str, timeout: int = 6) -> str:
    """Fetch an endpoint, tunneling over SSH if configured, otherwise direct."""
    url = server["base_url"].rstrip("/") + endpoint
    ssh_host = server.get("ssh_host")
    if ssh_host and not ssh_host.startswith("<"):
        return fetch_via_ssh(ssh_host, url, timeout)
    return fetch_text(url, timeout)


# ---------------------------------------------------------------------------
# Health / model parsing
# ---------------------------------------------------------------------------

def check_server(
    server: dict[str, Any],
) -> dict[str, Any]:
    """Return server status dict after probing."""
    result = {
        "name": server["name"],
        "host": server.get("host", "?"),
        "label": server.get("label", "?"),
        "type": server.get("type", "openai"),
        "online": False,
        "models": [],
        "health": None,
        "error": None,
        "description": server.get("description", ""),
        "base_url": server["base_url"],
    }

    # Skip servers with unconfigured SSH hosts
    if server.get("ssh_host", "").startswith("<"):
        result["error"] = "SSH host not configured → duplicate template into config.json"
        return result

    # Health
    health_ep = server.get("health_endpoint")
    if health_ep:
        health_text = fetch_safe(server, health_ep, timeout=4)
        if health_text.startswith("ERROR"):
            result["error"] = health_text
            return result
        try:
            result["health"] = json.loads(health_text)
        except json.JSONDecodeError:
            result["health"] = {"raw": health_text[:200]}

    # Models
    models_ep = server.get("models_endpoint")
    if models_ep:
        models_text = fetch_safe(server, models_ep, timeout=6)
        if models_text.startswith("ERROR"):
            # If health succeeded but models fail, server is partially up
            if not result["error"]:
                result["error"] = models_text
            return result

        try:
            models_data = json.loads(models_text)
        except json.JSONDecodeError:
            result["error"] = f"Non-JSON response from {models_ep}"
            return result

        srv_type = server.get("type", "openai")
        if srv_type == "ollama":
            result["models"] = [
                m.get("name", "?") for m in models_data.get("models", [])
            ]
        elif srv_type == "openai":
            result["models"] = [
                m.get("id", "?") for m in models_data.get("data", [])
            ]
        else:
            result["models"] = models_data.get("models", [])

    result["online"] = result["error"] is None
    return result


def check_all(servers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    servers = list(servers)
    for srv in servers:
        yield check_server(srv)


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

def json_bytes(
    payload: dict[str, Any], status: int = 200
) -> tuple[int, bytes]:
    return status, json.dumps(payload, indent=2).encode("utf-8")


class Handler(SimpleHTTPRequestHandler):
    server_version = "ModelDashboard/1.0"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {fmt % args}")

    def send_payload(
        self, status: int, data: bytes, content_type: str
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            self.send_payload(200, b'{"ok":true}', "application/json")
            return

        if parsed.path == "/api/servers":
            cfg = load_config()
            results = list(check_all(cfg.get("servers", [])))
            self.send_payload(
                200,
                json.dumps(
                    {
                        "generatedAt": time.strftime(
                            "%Y-%m-%dT%H:%M:%S%z"
                        ),
                        "title": cfg.get("title", "Model Servers"),
                        "servers": results,
                    }
                ).encode("utf-8"),
                "application/json",
            )
            return

        if parsed.path == "/api/refresh-interval":
            cfg = load_config()
            self.send_payload(
                200,
                json.dumps(
                    {"interval": cfg.get("refreshInterval", 30)}
                ).encode("utf-8"),
                "application/json",
            )
            return

        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    STATIC.mkdir(exist_ok=True)

    # Warn if config is just the template
    if not CONFIG_PATH.exists() and DEFAULT_CONFIG_SAMPLE.exists():
        cfg = json.loads(DEFAULT_CONFIG_SAMPLE.read_text())
        for srv in cfg.get("servers", []):
            if srv.get("ssh_host", "").startswith("<"):
                print(
                    f"  [config] {srv['name']}: unconfigured SSH host "
                    f"'{srv['ssh_host']}' – "
                    f"cp config.template.json config.json and edit"
                )

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Model Server Dashboard listening on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping Model Server Dashboard")


if __name__ == "__main__":
    sys.exit(main())
