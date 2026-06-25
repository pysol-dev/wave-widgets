# research-cockpit - Agent setup

This widget is a local Wave web-widget control plane for human-guided research sessions. It stores session state locally, validates source URLs, and returns same-tab links or copyable commands. It does not automate browsers, call undocumented Hermes APIs, or depend on `WAVETERM_JWT` from LaunchAgent context.

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
cd research-cockpit
sh install.sh
```

This will:

1. Copy `config.template.json` to `config.json` if needed
2. Create the local `state/` directory for persisted session JSON
3. Generate and load a LaunchAgent (`wave.widgets.research-cockpit`)
4. Start the backend on `http://127.0.0.1:8792`
5. Add a `Research` direct web widget to `/Users/<user>/.config/waveterm/widgets.json`

## Configure profiles and workflows

Edit `research-cockpit/config.json` after install. The file owns workflow phases, worker profile labels, source types, and copyable command templates. Keep private prompts, credentials, API keys, and tokens out of this repository and out of source URLs.

The backend uses the config as data. It does not hard-code a swarm, model choice, Hermes integration, or deterministic Wave adjacency helper.

## API surface

Useful endpoints:

```sh
curl http://127.0.0.1:8792/api/health
curl http://127.0.0.1:8792/api/config | python3 -m json.tool
curl http://127.0.0.1:8792/api/state | python3 -m json.tool
curl http://127.0.0.1:8792/api/sources | python3 -m json.tool
```

Add a source:

```sh
curl -X POST http://127.0.0.1:8792/api/sources \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/research-source","title":"Example source"}'
```

Patch session state:

```sh
curl -X PATCH http://127.0.0.1:8792/api/state \
  -H 'Content-Type: application/json' \
  -d '{"session":{"question":"What evidence answers the research brief?","phase":"survey"}}'
```

## Same-tab opening and commands

The `/open/source/<id>` path redirects the current Wave web pane to a saved source URL after validation. Source records also include a `waveWebOpenCommand` string that can be copied into a Wave-aware terminal if the operator wants to open a separate web pane manually.

The LaunchAgent never runs `wsh`, never assumes `WAVETERM_JWT`, and never calls undocumented Wave or Hermes APIs.

## Persistent state

State is stored at `research-cockpit/state/session.json` by default. This file is user-owned runtime data and is ignored by the widget-local `.gitignore`.

## Troubleshooting

- Server logs: `research-cockpit/launchd.out.log`
- LaunchAgent status: `launchctl print gui/$(id -u)/wave.widgets.research-cockpit`
- Restart: `launchctl kickstart -k gui/$(id -u)/wave.widgets.research-cockpit`
- If a source URL validation fails, remove placeholders, credentials, token-like query parameters, or unsupported schemes.
