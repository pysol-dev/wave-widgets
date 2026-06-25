# Hermes Workspace Widget

Status: planned. This directory is intentionally README-only until implementation starts.

## Purpose

This subproject captures a Wave Terminal widget direction for Hermes Workspace as a browser/web app surface. The researched distinction is that Hermes Workspace is a workspace UI, not the Herm terminal/TUI surface. The natural Wave shape is a `view: "web"` widget that opens the workspace app in a Wave web pane.

The widget should make the workspace UI easy to open from Wave without pretending to be the official Herm terminal pane.

## Proposed Wave shape

Use a web widget that points directly at a local or configured workspace URL.

```json
{
  "hermes-workspace": {
    "icon": "layout-dashboard",
    "label": "Hermes Workspace",
    "blockdef": {
      "meta": {
        "view": "web",
        "url": "http://127.0.0.1:<port>",
        "pinnedurl": "http://127.0.0.1:<port>"
      }
    }
  }
}
```

The exact URL, port, startup command, and backend shape should come from the Hermes Workspace source project at implementation time. This README does not claim any workspace API, authentication flow, data model, or Wave-specific bridge.

## Coexistence with the official Herm terminal pane

Herm and Hermes Workspace should sit side by side in Wave:

* The official Herm terminal pane remains the terminal/TUI path.
* This widget opens the workspace browser UI.
* Users can place the terminal pane and workspace pane next to each other when that workflow is useful.

This keeps the official terminal experience intact while adding a separate workspace surface for tasks that belong in a web UI.

## Why this is separate from Herm and HUDUI

Hermes Workspace is a web app/workspace UI. Herm is terminal/TUI oriented, and Hermes HUDUI is a separate web app/HUD UI. Keeping each one as its own widget matches the Wave widget model, where each top-level directory is a standalone app with its own lifecycle, install path, and config.

One all-in-one widget would force unrelated surfaces into one project. That would make terminal launch behavior, web app hosting, and HUD presentation depend on each other for no clear benefit.

A launcher or meta-widget could be added later to open the Herm terminal widget, Hermes Workspace, and Hermes HUDUI from one place. That launcher should not replace these standalone subprojects.

## Feasibility notes

* Wave supports URL-based web widgets with `view: "web"`, `url`, and `pinnedurl`.
* A local backend may be useful if the workspace app needs to be served locally before Wave opens it.
* The service should bind to `127.0.0.1` unless a source project requirement says otherwise.
* This plan does not assume full browser automation, extension support, or hidden Wave webview control.
* No port is reserved yet.

## Implementation questions

* Does Hermes Workspace ship as a local web server, static app, or remote URL?
* What startup command and health check does the source project document?
* Does it need a LaunchAgent, or can the widget point at a user-managed workspace URL?
