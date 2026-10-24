# wave-port-map — Agent setup

One-shot setup for Wave Terminal. Run these commands from the repo root.

## Prerequisites

```sh
# Wave Terminal must be installed
test -d /Applications/Wave.app || echo "Install Wave Terminal first"

# Python 3.10+
python3 --version
```

## Install

```sh
# From repo root
cd wave-port-map
./install.sh
```

This will:

1. Copy `config.template.json` → `config.json` if needed
2. Generate and load a LaunchAgent (`wave.widgets.wave-port-map`)
3. Start the server on `http://127.0.0.1:8795`
4. Add a `Port Map` web widget to `/Users/<user>/.config/waveterm/widgets.json`

## Open in Wave

Click the **Port Map** icon (diagram-project) in the Wave sidebar. A Mermaid diagram of active TCP listeners appears with clickable nodes for Kill and Send to Terminal actions.

## Verify

```sh
curl http://127.0.0.1:8795/api/health
# → {"ok": true}

curl http://127.0.0.1:8795/api/ports | python3 -m json.tool | head -10
# → {"generatedAt": "...", "count": N, ...}
```

## Troubleshooting

- Server logs: `wave-port-map/launchd.out.log`
- LaunchAgent status: `launchctl print gui/$(id -u)/wave.widgets.wave-port-map`
- Restart: `launchctl kickstart -k gui/$(id -u)/wave.widgets.wave-port-map`
