# Oh My OpenCode Control Pane

This directory is a docs first scaffold for a planned Wave Terminal widget. The goal is a local control pane for Oh My OpenCode and OpenCode, shown inside Wave as a custom web UI backed by a local service.

This is not meant to be a simple stock web widget that points at an existing URL. The useful version needs its own backend because it will need to read local configuration, inspect runtime state, normalize several kinds of OpenCode and Oh My OpenCode data, and present safe actions in one place.

## Planning Position

The working conclusion from the current Wave widget research is that Wave is strongest as a local operating surface for terminals, dashboards, preview panes, and control panels. Stock web widgets are good for fixed URLs and local app launchers. More capable workflows need a local backend plus a custom web UI.

An OpenCode control pane fits that stronger pattern. It is a human operated cockpit for a local developer environment, not a generic browser automation surface. It should show what is running, what is configured, what changed recently, and which actions are safe to take from a sidebar widget.

The widget should avoid pretending that uninspected Oh My OpenCode APIs exist. Until the implementation has inspected the real config files, plugin behavior, CLI commands, and any runtime sockets or logs, the backend should be described as an adapter layer over verified local sources.

## Why This Fits a Local Backend Widget

- It needs to combine several local data sources, including OpenCode config, Oh My OpenCode config, agent files, plugin state, MCP definitions, session metadata, and local logs.
- It needs a safer permission boundary than a pure web page. The backend can decide which files are read only, which actions require confirmation, and which actions are out of scope.
- It should work next to active terminal panes. Wave can keep the control surface beside OpenCode, shell sessions, logs, and project panes.
- It benefits from quick refresh loops. The UI can poll a local backend for status without exposing private details to a remote service.
- It can start read only, then add carefully scoped actions later.

## Proposed Tabs

### Sessions

Show active and recent OpenCode sessions, their working directories, timestamps, agent usage, and high level status. Keep paths PII safe in any exported artifacts, for example `$HOME/project` or `/Users/<user>/project`.

Planned read only views:

- Current session summary.
- Recent sessions grouped by project.
- Active background tasks where verified sources expose them.
- Links or copyable commands to reopen relevant local context.

### MCPs

Show configured MCP servers and their local health state. The first pass should not assume a standard health API. It should report what can be verified from configuration and process checks.

Planned read only views:

- MCP name and source config file.
- Command or transport type, redacted where needed.
- Enabled status if the inspected config supports that concept.
- Last known error source if available from logs.

### Skills

Show installed skills, their names, descriptions, and source locations. This should help answer which skill will load for a task and where duplicate or overlapping skills live.

Planned read only views:

- Skill inventory.
- Scope or source, such as user, project, or built in, only where verified.
- Description preview.
- Missing or duplicated names.

### Plugins

Show Oh My OpenCode and OpenCode plugin entries that have been verified from local config. This tab should be careful because plugin removal or replacement can disrupt the current setup.

Planned read only views:

- Plugin name.
- Source of truth config location.
- Compatibility or bootstrap shim notes when present.
- Warnings for entries that look disabled, missing, or shadowed, without changing them.

### LSPs

Show language server related configuration and status where it can be observed safely.

Planned read only views:

- Known configured language servers.
- Recent diagnostics counts by workspace if available.
- Links or copyable commands for manual checks.
- Clear unknown states when no source has been inspected.

### Slash Commands

Show available slash commands and where they come from. This should help with discovery and prevent confusion between project, user, and built in commands.

Planned read only views:

- Command name.
- Description.
- Scope.
- Backing file or package, redacted for exports.

### Memory

Show durable instruction and memory sources that affect OpenCode behavior. This includes files such as agent instructions, config comments, and session notes only after the implementation confirms exact paths and meanings.

Planned read only views:

- Loaded instruction files.
- Session notes presence and freshness.
- High level summary of which files shape behavior.
- No secret values or raw private paths in exported output.

### Cron and Jobs

Show scheduled or long running local jobs related to the OpenCode setup, if verified. This can include LaunchAgents, recurring scripts, or background watchers.

Planned read only views:

- Job label.
- Source plist or config file.
- Last observed state.
- Log file pointers with PII safe display.

### Metrics

Show local health and usage signals. Keep this practical, not analytics heavy.

Planned read only views:

- Backend health.
- Config freshness.
- Count of sessions, skills, MCPs, plugins, and commands detected.
- Error counts from verified local logs.

### Artifacts

Collect generated reports and safe snapshots. This tab should make it easy to inspect what the control pane produced without storing secrets.

Planned read only views:

- Exported summaries.
- Diagnostics bundles with redaction.
- Links to local report files.
- Clear labels for generated versus source files.

## Recommended Architecture

- Build a small local backend bound to `127.0.0.1` on a deterministic port chosen during implementation.
- Serve a custom web UI from that backend and register it as a Wave web widget with `view: "web"`, `url`, and `pinnedurl`.
- Keep the backend read only for the MVP. Add write actions later only after each action has a clear confirmation flow and rollback story.
- Use adapters for each source type: OpenCode config, Oh My OpenCode config, agents, skills, MCPs, logs, sessions, LaunchAgents, and artifacts.
- Treat config comments as part of the contract. Display them when helpful, but do not rewrite config from this widget in the first version.
- Redact private paths, hostnames, tokens, and usernames in any export or artifact. Use examples like `/Users/<user>/project`, `<hostname>`, and `<token>`.
- Keep source discovery explicit. If a source has not been inspected, the UI should say `unknown` rather than guessing.

## MVP

The first useful version should be a read only dashboard with a local backend and a Wave web UI.

MVP scope:

- Health page for the widget backend.
- Inventory tabs for sessions, MCPs, skills, plugins, LSPs, slash commands, memory, cron and jobs, metrics, and artifacts.
- Source path display with PII safe rendering.
- Refresh button for reloading local state.
- Exportable redacted summary for debugging the setup.
- Clear `unknown` states when the backend has not inspected a source or cannot verify a runtime claim.

Not in MVP:

- Editing OpenCode or Oh My OpenCode config.
- Removing, disabling, or replacing plugins.
- Restarting OpenCode, Wave, tmux, Moshi, MCP servers, or LaunchAgents.
- Claiming support for unverified Oh My OpenCode APIs.
- Browser automation, extension workflows, or remote analytics.

## Open Questions

- Which local files are the source of truth for each OpenCode and Oh My OpenCode setting the widget should show?
- Which session data is safe and stable enough to read from a local backend?
- Does Oh My OpenCode expose any supported CLI or runtime interface for status, or should the first version rely only on files and process checks?
- Which actions, if any, are safe enough for a later version, and what confirmation should they require?
- What redaction rules should apply to local artifacts beyond usernames, hostnames, tokens, and absolute paths?
- Which deterministic port should this widget use so it does not collide with existing Wave widgets?
- Should artifacts live inside the widget directory, a user data directory, or a separate ignored local folder?

## Safety Notes

- Keep the first version local only.
- Prefer read only inspection until the real data sources are mapped.
- Do not store credentials, tokens, raw private paths, hostnames, or machine names in committed files.
- Do not disrupt the current OpenCode, tmux, Moshi, or Wave session from this widget without a durable note and explicit user approval.
