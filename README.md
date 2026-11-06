# Wave Widgets

A collection of custom widgets for [Wave Terminal](https://waveterm.dev/).

## Widgets included

- **Port Map** — Visual diagram of active TCP listeners on your Mac, with process names, PIDs, and quick actions (Kill, Send to Terminal).
- **Model Server Dashboard** — Status dashboard for local and remote model servers (Ollama, LM Studio, llama.cpp, Kokoro TTS, vLLM, etc.) with health checks, model listings, and per-server actions.
- **n8n** — Opens the native n8n UI for local/community or paid/cloud instances, with the target URL set in local widget config.

## Requirements

- macOS with Wave Terminal installed
- Python 3.10+
- For remote servers: SSH access configured (Tailscale recommended)

## Installation

Each widget has its own install script. Run from the widget directory:

```bash
cd wave-port-map
./install.sh
```

This registers a LaunchAgent so the widget server starts at login, and updates `widgets.json` to add the Wave sidebar button.

## Adding to Wave

After installation, click the widget's icon in the Wave sidebar to open it. Web widgets open automatically as native Wave web panes.

## Configuration

Widget-specific configuration is in `config.json` files **inside their directories**, which are gitignored. Use `config.template.json` as a starting point and copy it to populate your own endpoints.

The n8n widget reads its instance URL from local config so it can point at either a self-hosted/community install or a paid/cloud n8n instance.

## Security

- Widget backends bind to `127.0.0.1` only.
- Remote servers are accessed over SSH (Tailscale or local). No credentials are stored in this repo.
- No PII or secrets should ever be committed — see [AGENTS.md](AGENTS.md) for redaction rules.

## Semanticore control-plane integration

Wave Widgets is an independently versioned monorepo that can participate in a Semanticore workspace. It owns Wave Terminal presentation; governance/effect authority belongs to the implemented backend such as GitGov. See [the component integration contract](docs/semanticore-integration.md) for issue/PR ownership, private-data boundaries and safe coexistence with an existing live checkout.
