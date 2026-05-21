# Wave Widgets Monorepo

## Repository scope

This repo contains independent Wave Terminal widget applications. Each widget lives in its own directory at the top level. Widgets are standalone — they do not share code, dependencies, or build tooling.

## Adding a widget

1. Create a new directory at repo root, e.g. `my-widget/`.
2. Each widget needs its own server entrypoint, static assets, and an `install.sh` that registers the LaunchAgent and optionally updates `widgets.json`.
3. Document the widget in this file's "Widgets" section.

## Widgets

| Directory | Description | Port | LaunchAgent |
|---|---|---|---|
| `wave-port-map/` | Visual map of active TCP ports with Mermaid diagram | 8765 | `com.thales.wave-port-map` |
| `model-server-dashboard/` | Dashboard for local and remote model servers | 8787 | `com.thales.model-server-dashboard` |
| `n8n-launcher/` | Opens the native n8n UI for local/community or cloud instances via local config | 8791 | `com.thales.n8n-launcher` |

## PII redaction — MANDATORY

This repository is **public**. Never commit personally identifiable information or secrets.

**What counts as PII (non-exhaustive):**

- IP addresses (private, public, Tailscale/CGNAT)
- Usernames on production or remote systems
- Hostnames, FQDNs, or machine names
- File paths containing a real username (e.g. `/Users/alice/...` should be `/Users/<user>/...`)
- SSH private keys, API tokens, passwords
- Cloud resource identifiers (AWS account IDs, instance IDs, etc.)
- Geolocation data
- Real names, email addresses
- Internal network topology (e.g. Tailscale IP ranges, VPN endpoints)

**When writing or modifying any file in this repo:**

- Replace IP addresses with `x.x.x.x` or descriptive placeholders.
- Replace real usernames with `<user>`, `<username>`, or a descriptive role.
- Replace real hostnames with `<hostname>` or `<machine>`.
- Replace absolute file paths containing a real username: use `/Users/<user>/...` or `$HOME/...`.
- Never include `.env`, `config.json` (only `config.template.json`), `*.key`, `*.pem`, or credential files.
- Never include SSH config files, `known_hosts`, or `authorized_keys`.

**Tools to help:**

- Before committing, run: `git diff --cached` and review for IPs, usernames, and paths.
- Use `git secrets` or a pre-commit hook if you work on this repo frequently.
- When in doubt, ask the user before committing something sensitive.
