# Plannotator in Wave

Open Plannotator plans, code reviews, and annotations in a native Wave Terminal
web pane. The agent terminal stays open beside the review.

## Install

From this directory:

```sh
sh install.sh
```

The installer copies `plannotator-wave-open` to `$HOME/.local/bin` and sets
`PLANNOTATOR_BROWSER` in `$HOME/.zshenv`. This includes non-interactive zsh
launchers. Existing shell configuration is preserved; rerunning the installer
does not duplicate the setting.

For the current shell:

```sh
export PLANNOTATOR_BROWSER="$HOME/.local/bin/plannotator-wave-open"
```

Launch OmO or Senpi from a Wave terminal pane so its Plannotator extension
inherits that environment and Wave's authenticated session. An already running
agent must already have the variable or be started again to inherit it.

Install the official extension into the profile you use:

```sh
omo install npm:@plannotator/pi-extension
# For standalone Senpi instead:
senpi install npm:@plannotator/pi-extension
```

In that agent session, use `/plannotator-plan-mode`,
`/plannotator-review`, or `/plannotator-annotate`.

## How it works

Plannotator calls the executable named by `PLANNOTATOR_BROWSER` with its review
URL. The helper passes that URL as one argument to `wsh web open`, which creates
a native web block. It never replaces the agent's terminal block or launches an
external browser. Review decisions return through Plannotator's existing
connection to the agent.

Plannotator supplies the HTTP server and chooses its review port. This
integration therefore needs no additional server, fixed port, LaunchAgent, or
sidebar widget. It opens the actual review directly instead of wrapping it in a
second dashboard.

Wave session authentication is required. Running from an ordinary terminal or
a detached background service may fail; the helper reports the Wave CLI error
instead of silently opening an external browser. On macOS it also finds Wave's
bundled CLI when `wsh` is absent from `PATH`.

## Check

```sh
sh test.sh
```

This checks installation in a temporary home, including paths containing spaces,
preservation of existing shell settings, reinstall behavior, and invalid input.

For a live test, run a Plannotator review from inside Wave, send a recognizable
comment in the web pane, and check that it reaches the originating agent.
