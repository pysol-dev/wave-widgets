#!/bin/sh
# Install the opener used by both the Plannotator CLI and its Pi extension.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEST="$HOME/.local/bin/plannotator-wave-open"
SHELL_CONFIG="$HOME/.zshenv"
EXPORT_LINE='export PLANNOTATOR_BROWSER="$HOME/.local/bin/plannotator-wave-open"'

mkdir -p "$(dirname "$DEST")"
install -m 0755 "$ROOT/plannotator-wave-open" "$DEST"

# zsh reads .zshenv for non-interactive shells too, including agent launchers.
# Keep existing shell configuration and do not duplicate this setting on reinstall.
if [ ! -f "$SHELL_CONFIG" ] || ! grep -Fxq "$EXPORT_LINE" "$SHELL_CONFIG"; then
  printf '\n%s\n%s\n' \
    '# Open Plannotator reviews in Wave Terminal web panes.' \
    "$EXPORT_LINE" >> "$SHELL_CONFIG"
fi

printf '%s\n' \
  "Installed $DEST" \
  'New zsh sessions will use the Wave opener.' \
  'For an existing shell, run:' \
  "$EXPORT_LINE"
