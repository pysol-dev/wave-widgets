# n8n-launcher - Agent setup

This widget is a small Wave web-widget launcher for native n8n UIs. It does not implement a workflow editor; it opens the official n8n UI for local/community, self-hosted, or paid cloud instances.

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
cd n8n-launcher
sh install.sh
```

This will:

1. Copy `config.template.json` to `config.json` if needed
2. Generate and load a LaunchAgent (`com.thales.n8n-launcher`)
3. Start the launcher on `http://127.0.0.1:8791`
4. Add an `n8n` web widget to `/Users/<user>/.config/waveterm/widgets.json`

## Configure instances

Edit `n8n-launcher/config.json` after install.

The default local/community n8n URL is:

```json
{
  "id": "local",
  "name": "Local n8n",
  "url": "http://127.0.0.1:5678",
  "kind": "local",
  "enabled": true,
  "description": "Default local/community n8n UI"
}
```

For paid/cloud or remote/community n8n, replace placeholder URLs in `config.json` and set `enabled` to `true`. Keep credentials, API keys, and tokens out of URLs.

## Open in Wave

Click the **n8n** widget in the Wave sidebar. The launcher lists enabled and placeholder instances. Click **Open n8n UI** to navigate the Wave web pane to the official n8n UI.

## Verify

```sh
curl http://127.0.0.1:8791/api/health
# -> {"ok": true}

curl http://127.0.0.1:8791/api/config | python3 -m json.tool
# -> launcher title and configured instances
```

## Troubleshooting

- Server logs: `n8n-launcher/launchd.out.log`
- LaunchAgent status: `launchctl print gui/$(id -u)/com.thales.n8n-launcher`
- Restart: `launchctl kickstart -k gui/$(id -u)/com.thales.n8n-launcher`
- If a cloud or remote card says the URL still contains a placeholder, edit `config.json` and remove all angle-bracket placeholders.
