#!/bin/sh
# Install model-server-dashboard as a LaunchAgent and register in Wave widgets.json
set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"
PLIST_SRC="${ROOT}/com.thales.model-server-dashboard.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/com.thales.model-server-dashboard.plist"
WIDGETS_JSON="${HOME}/.config/waveterm/widgets.json"
PORT="${MODEL_DASHBOARD_PORT:-8787}"

# Copy config template if config.json doesn't exist
if [ ! -f "${ROOT}/config.json" ] && [ -f "${ROOT}/config.template.json" ]; then
  cp "${ROOT}/config.template.json" "${ROOT}/config.json"
  echo "Copied config.template.json → config.json — edit it with your servers."
fi

# Generate plist
cat > "${PLIST_SRC}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.thales.model-server-dashboard</string>
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
launchctl kickstart -k "gui/$(id -u)/com.thales.model-server-dashboard"

# Ensure widgets.json entry
if [ -f "${WIDGETS_JSON}" ]; then
  python3 -c "
import json, sys
with open('${WIDGETS_JSON}') as f: cfg = json.load(f)
cfg['model-server-dashboard'] = {
  'icon': 'microchip',
  'label': 'Models',
  'blockdef': {
    'meta': {
      'view': 'web',
      'url': 'http://127.0.0.1:${PORT}',
      'pinnedurl': 'http://127.0.0.1:${PORT}'
    }
  }
}
with open('${WIDGETS_JSON}', 'w') as f: json.dump(cfg, f, indent=2)
" 2>/dev/null || echo "Warning: could not update widgets.json"
fi

echo "model-server-dashboard installed. Open Models from Wave sidebar."
