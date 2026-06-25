#!/bin/sh
# Install research-cockpit as a LaunchAgent and register in Wave widgets.json.
set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"
LABEL="wave.widgets.research-cockpit"
PLIST_SRC="${ROOT}/${LABEL}.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/${LABEL}.plist"
WIDGETS_JSON="${HOME}/.config/waveterm/widgets.json"
PORT="${RESEARCH_COCKPIT_PORT:-8792}"

if [ ! -f "${ROOT}/config.json" ] && [ -f "${ROOT}/config.template.json" ]; then
  cp "${ROOT}/config.template.json" "${ROOT}/config.json"
  echo "Copied config.template.json to config.json. Edit it to customize profiles and workflows."
fi

mkdir -p "${ROOT}/state"

cat > "${PLIST_SRC}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>${ROOT}/server.py</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <dict>
    <key>SuccessfulExit</key>
    <false/>
  </dict>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>RESEARCH_COCKPIT_PORT</key>
    <string>${PORT}</string>
  </dict>
  <key>StandardOutPath</key>
  <string>${ROOT}/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>${ROOT}/launchd.err.log</string>
</dict>
</plist>
EOF

mkdir -p "$(dirname "${PLIST_DST}")"
cp "${PLIST_SRC}" "${PLIST_DST}"

launchctl bootstrap "gui/$(id -u)" "${PLIST_DST}" 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/${LABEL}"

mkdir -p "$(dirname "${WIDGETS_JSON}")"
WIDGETS_JSON_PATH="${WIDGETS_JSON}" RESEARCH_COCKPIT_PORT_VALUE="${PORT}" python3 <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["WIDGETS_JSON_PATH"])
port = os.environ["RESEARCH_COCKPIT_PORT_VALUE"]
if path.exists():
    cfg = json.loads(path.read_text())
else:
    cfg = {}

cfg["research-cockpit"] = {
    "icon": "diagram-project",
    "label": "Research",
    "blockdef": {
        "meta": {
            "view": "web",
            "url": f"http://127.0.0.1:{port}",
            "pinnedurl": f"http://127.0.0.1:{port}",
        }
    },
}
path.write_text(json.dumps(cfg, indent=2) + "\n")
PY

echo "research-cockpit installed. Open Research from the Wave sidebar."
