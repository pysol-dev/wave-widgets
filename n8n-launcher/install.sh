#!/bin/sh
# Install n8n-launcher as a LaunchAgent and register in Wave widgets.json
set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.thales.n8n-launcher"
PLIST_SRC="${ROOT}/${LABEL}.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/${LABEL}.plist"
WIDGETS_JSON="${HOME}/.config/waveterm/widgets.json"
PORT="${N8N_LAUNCHER_PORT:-8791}"

if [ ! -f "${ROOT}/config.json" ] && [ -f "${ROOT}/config.template.json" ]; then
  cp "${ROOT}/config.template.json" "${ROOT}/config.json"
  echo "Copied config.template.json to config.json. Edit it to add cloud or remote n8n URLs."
fi

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

if [ -f "${WIDGETS_JSON}" ]; then
  python3 -c "
import json
path = '${WIDGETS_JSON}'
with open(path) as f:
    cfg = json.load(f)
cfg['n8n-launcher'] = {
    'icon': 'diagram-project',
    'label': 'n8n',
    'blockdef': {
        'meta': {
            'view': 'web',
            'url': 'http://127.0.0.1:${PORT}',
            'pinnedurl': 'http://127.0.0.1:${PORT}'
        }
    }
}
with open(path, 'w') as f:
    json.dump(cfg, f, indent=2)
" 2>/dev/null || echo "Warning: could not update widgets.json"
fi

echo "n8n-launcher installed. Open n8n from the Wave sidebar."
