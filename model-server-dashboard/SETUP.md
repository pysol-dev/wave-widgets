# model-server-dashboard — Agent setup

One-shot setup for Wave Terminal. Run these commands from the repo root.

## Prerequisites

```sh
# Wave Terminal must be installed
test -d /Applications/Wave.app || echo "Install Wave Terminal first"

# Python 3.10+
python3 --version

# For remote server detection: SSH to remote hosts (e.g. brodex via Tailscale)
ssh -o ConnectTimeout=5 <remote-host> hostname 2>/dev/null || echo "Configure SSH for remote hosts in ~/.ssh/config"
```

## Install

```sh
# From repo root
cd model-server-dashboard
./install.sh
```

This will:

1. Copy `config.template.json` → `config.json`
2. Generate and load a LaunchAgent (`com.thales.model-server-dashboard`)
3. Start the server on `http://127.0.0.1:8787`
4. Add a `Models` web widget to `/Users/<user>/.config/waveterm/widgets.json`

## Configure remote servers

Edit `model-server-dashboard/config.json`:

```sh
cd model-server-dashboard
cp config.template.json config.json
# Edit config.json with your remote SSH host
# Set ssh_host to your SSH config alias for any remote servers
# Placeholder values are marked with angle brackets: <remote-host>
```

### Example: brodex via Tailscale

If your SSH config has `Host brodex` with a Tailscale IP:

```json
{
  "name": "llama.cpp / vLLM",
  "host": "brodex",
  "label": "LLM",
  "base_url": "http://127.0.0.1:8000",
  "type": "openai",
  "models_endpoint": "/v1/models",
  "ssh_host": "brodex",
  "description": "Remote GPU inference"
}
```

## Open in Wave

Click the **Models** icon (microchip) in the Wave sidebar. Server cards appear grouped by host, showing online/offline status, loaded models, and action buttons.

## Verify

```sh
curl http://127.0.0.1:8787/api/health
# → {"ok": true}

curl http://127.0.0.1:8787/api/servers | python3 -m json.tool | head -20
# → {"generatedAt": "...", "servers": [...]}
```

## Troubleshooting

- Server logs: `model-server-dashboard/launchd.out.log`
- LaunchAgent status: `launchctl print gui/$(id -u)/com.thales.model-server-dashboard`
- Restart: `launchctl kickstart -k gui/$(id -u)/com.thales.model-server-dashboard`
- SSH remote checks use the host's `~/.ssh/config` and SSH agent — ensure both are available to the LaunchAgent process.
