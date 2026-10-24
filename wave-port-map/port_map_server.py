#!/usr/bin/env python3
"""Local Wave Terminal widget server for visualizing active listening ports."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = int(os.environ.get("WAVE_PORT_MAP_PORT", "8795"))
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
WSH_BIN = os.environ.get(
    "WSH_BIN",
    os.path.expanduser(
        "~/Library/Application Support/waveterm/bin/wsh"
    ),
)


def run_text(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            args,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"ERROR: {exc}"
    return completed.stdout if completed.stdout.strip() else completed.stderr


def describe_command(command: str) -> str:
    lowered = command.lower()
    descriptions = [
        ("plannotator", "Plannotator review or annotation server"),
        ("opencode", "OpenCode local agent or control server"),
        ("wavesrv", "Wave Terminal backend service"),
        ("syncthing", "Syncthing file synchronization service"),
        ("ssh", "SSH tunnel or forwarded port"),
        ("raycast", "Raycast desktop helper service"),
        ("figma", "Figma desktop agent"),
        ("rapportd", "Apple device continuity service"),
        ("openchamber", "OpenChamber local service"),
        ("discord", "Discord desktop app or helper service"),
        ("node", "Node.js or JavaScript development server"),
        ("python", "Python web app, notebook, or API server"),
        ("ruby", "Ruby application server"),
        ("rails", "Ruby on Rails application"),
        ("java", "Java service"),
        ("docker", "Docker container proxy or service"),
        ("postgres", "PostgreSQL database"),
        ("mysql", "MySQL database"),
        ("redis", "Redis cache/server"),
        ("nginx", "Nginx web server"),
        ("httpd", "Apache web server"),
        ("chrome", "Browser helper or debugging endpoint"),
        ("electron", "Electron desktop app"),
        ("ollama", "Ollama local model server"),
        ("lm studio", "LM Studio local model server"),
    ]
    for needle, description in descriptions:
        if needle in lowered:
            return description
    return "Local process listening for network connections"


def parse_lsof_line(line: str) -> dict[str, Any] | None:
    parts = line.split()
    if len(parts) < 9 or not parts[1].isdigit():
        return None

    name = " ".join(parts[8:])
    match = re.search(r":(\d+)(?:\s|$|\s*\()", name)
    if not match:
        return None

    port = int(match.group(1))
    address = name.split(" (LISTEN)", 1)[0]
    command = parts[0]
    pid = int(parts[1])
    user = parts[2]
    details = run_text(["ps", "-p", str(pid), "-o", "command="]).strip()

    return {
        "id": f"port-{port}-pid-{pid}",
        "port": port,
        "pid": pid,
        "user": user,
        "command": command,
        "description": describe_command(f"{command} {details}"),
        "address": address,
        "details": details or command,
    }


def active_ports() -> list[dict[str, Any]]:
    output = run_text(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"])
    by_process: dict[tuple[int, int], dict[str, Any]] = {}
    for line in output.splitlines()[1:]:
        parsed = parse_lsof_line(line)
        if not parsed:
            continue
        key = (parsed["port"], parsed["pid"])
        existing = by_process.get(key)
        if existing:
            addresses = set(existing["address"].split(", "))
            addresses.add(parsed["address"])
            existing["address"] = ", ".join(sorted(addresses))
            continue
        by_process[key] = parsed
    ports = list(by_process.values())
    return sorted(ports, key=lambda item: (item["port"], item["command"].lower()))


def mermaid_for(ports: list[dict[str, Any]]) -> str:
    lines = ["flowchart LR", '  machine["This Mac"]']
    if not ports:
        lines.append('  quiet["No listening TCP ports found"]')
        lines.append("  machine --> quiet")
        return "\n".join(lines)

    for item in ports:
        node_id = f"p{item['port']}_{item['pid']}"
        label = (
            f"Port {item['port']}<br/>{item['description']}<br/>"
            f"{item['command']} &middot; PID {item['pid']}"
        )
        safe_label = label.replace('"', "'")
        lines.append(f'  machine --> {node_id}["{safe_label}"]')
        lines.append(
            f'  click {node_id} call selectPort("{item["id"]}") "Open actions"'
        )
    return "\n".join(lines)


def json_bytes(payload: dict[str, Any], status: int = 200) -> tuple[int, bytes]:
    return status, json.dumps(payload, indent=2).encode("utf-8")


class Handler(SimpleHTTPRequestHandler):
    server_version = "WavePortMap/1.0"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")

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
            status, data = json_bytes({"ok": True})
            self.send_payload(status, data, "application/json")
            return
        if parsed.path == "/api/ports":
            ports = active_ports()
            status, data = json_bytes(
                {
                    "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "count": len(ports),
                    "ports": ports,
                    "mermaid": mermaid_for(ports),
                }
            )
            self.send_payload(status, data, "application/json")
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self.read_json()
            ports = active_ports()

            if parsed.path == "/api/kill":
                pid = int(payload.get("pid", 0))
                match = next(
                    (item for item in ports if item["pid"] == pid), None
                )
                if not match:
                    status, data = json_bytes(
                        {
                            "ok": False,
                            "error": "PID is not listening on a visible TCP port.",
                        },
                        404,
                    )
                elif pid == os.getpid():
                    status, data = json_bytes(
                        {
                            "ok": False,
                            "error": "Refusing to kill the widget server.",
                        },
                        400,
                    )
                else:
                    os.kill(pid, signal.SIGTERM)
                    status, data = json_bytes(
                        {
                            "ok": True,
                            "message": f"Sent SIGTERM to {match['command']} "
                            f"on port {match['port']} (PID {pid}).",
                        }
                    )
                self.send_payload(status, data, "application/json")
                return

            if parsed.path == "/api/open-terminal":
                port = int(payload.get("port", 0))
                match = next(
                    (item for item in ports if item["port"] == port), None
                )
                if not match:
                    status, data = json_bytes(
                        {"ok": False, "error": "That port is no longer active."},
                        404,
                    )
                elif not Path(WSH_BIN).exists():
                    status, data = json_bytes(
                        {
                            "ok": False,
                            "error": f"Wave CLI not found at {WSH_BIN}",
                        },
                        500,
                    )
                else:
                    pid = match["pid"]
                    command = (
                        f"echo 'Port {port}: {match['description']}'; "
                        f"echo 'Process: {match['command']} (PID {pid})'; "
                        f"echo; lsof -nP -iTCP:{port} -sTCP:LISTEN; "
                        f"echo; ps -p {pid} -o pid,ppid,user,command; "
                        "echo; echo 'You can inspect it here, "
                        "or run kill if you want to stop it.'; "
                        "exec ${SHELL:-/bin/zsh} -l"
                    )
                    subprocess.Popen(
                        [WSH_BIN, "run", "--cwd", str(Path.home()), "--command", command]
                    )
                    status, data = json_bytes(
                        {
                            "ok": True,
                            "message": f"Opened a Wave terminal for port {port}.",
                        }
                    )
                self.send_payload(status, data, "application/json")
                return

            status, data = json_bytes(
                {"ok": False, "error": "Unknown action."}, 404
            )
            self.send_payload(status, data, "application/json")
        except Exception as exc:
            status, data = json_bytes({"ok": False, "error": str(exc)}, 500)
            self.send_payload(status, data, "application/json")


def main() -> None:
    STATIC.mkdir(exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Wave Port Map listening on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping Wave Port Map")


if __name__ == "__main__":
    sys.exit(main())
