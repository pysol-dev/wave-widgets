#!/bin/sh
# Install wave-port-map as a LaunchAgent and register in Wave widgets.json
set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"
PLIST_SRC="${ROOT}/wave.widgets.wave-port-map.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/wave.widgets.wave-port-map.plist"
WIDGETS_JSON="${HOME}/.config/waveterm/widgets.json"
PORT="${WAVE_PORT_MAP_PORT:-8765}"

# Generate plist
cat > "${PLIST_SRC}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>wave.widgets.wave-port-map</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>${ROOT}/port_map_server.py</string>
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
launchctl kickstart -k "gui/$(id -u)/wave.widgets.wave-port-map"

# Ensure widgets.json entry exists (web widget)
if [ -f "${WIDGETS_JSON}" ]; then
  python3 -c "
import json, sys
with open('${WIDGETS_JSON}') as f: cfg = json.load(f)
cfg['port-map'] = {
  'icon': 'diagram-project',
  'label': 'Port Map',
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

echo "wave-port-map installed. Open Port Map from Wave sidebar."
