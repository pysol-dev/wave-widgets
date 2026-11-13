#!/bin/sh
# Exercise installation in an isolated home without changing the real Wave setup.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
TEST_HOME="$TMP/home with spaces"
mkdir -p "$TEST_HOME"
printf '%s\n' 'export KEEP_EXISTING_CONFIG=kept' > "$TEST_HOME/.zshenv"

for script in install.sh plannotator-wave-open test.sh; do
  sh -n "$ROOT/$script"
done

HOME="$TEST_HOME" sh "$ROOT/install.sh" >/dev/null
HOME="$TEST_HOME" sh "$ROOT/install.sh" >/dev/null
test -x "$TEST_HOME/.local/bin/plannotator-wave-open"
cmp "$ROOT/plannotator-wave-open" "$TEST_HOME/.local/bin/plannotator-wave-open"
test "$(grep -c '^export PLANNOTATOR_BROWSER=' "$TEST_HOME/.zshenv")" -eq 1
configured=$(HOME="$TEST_HOME" ZDOTDIR="$TEST_HOME" /bin/zsh -c 'printf "%s" "$PLANNOTATOR_BROWSER:$KEEP_EXISTING_CONFIG"')
test "$configured" = "$TEST_HOME/.local/bin/plannotator-wave-open:kept"

if "$TEST_HOME/.local/bin/plannotator-wave-open" file:///tmp/plan.md 2>/dev/null; then
  printf '%s\n' 'FAIL: accepted a non-web URL' >&2
  exit 1
else
  test "$?" -eq 64
fi
if "$TEST_HOME/.local/bin/plannotator-wave-open" 2>/dev/null; then
  printf '%s\n' 'FAIL: accepted a missing URL' >&2
  exit 1
else
  test "$?" -eq 64
fi

printf '%s\n' 'PASS: shell syntax, repeatable installation, preserved configuration, and URL validation'
