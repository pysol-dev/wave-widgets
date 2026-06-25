# Hermes HUDUI Widget

Status: planned. This directory is intentionally README-only until implementation starts.

## Purpose

This subproject captures a Wave Terminal widget direction for Hermes HUDUI as a browser/web app surface. The researched distinction is that HUDUI is a HUD-style UI, not the Herm terminal/TUI surface and not the broader Hermes Workspace UI. The natural Wave shape is a focused `view: "web"` widget.

The widget should provide a compact HUD pane inside Wave while leaving Herm terminal usage and Hermes Workspace usage to their own surfaces.

## Proposed Wave shape

Use a web widget that points directly at a local or configured HUDUI URL.

```json
{
  "hermes-hudui": {
    "icon": "gauge",
    "label": "Hermes HUDUI",
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

The exact URL, port, app server, and supported actions should come from the Hermes HUDUI source project at implementation time. This README does not claim specific HUD controls, event streams, APIs, or terminal integration.

## Coexistence with the official Herm terminal pane

Hermes HUDUI should complement, not replace, the official Herm terminal pane:

* The official Herm terminal pane stays responsible for terminal/TUI interaction.
* This widget opens the HUD UI in a browser pane.
* The HUD can be placed beside Herm or Hermes Workspace when users want status or control context nearby.

That separation lets the HUD stay focused and avoids turning a terminal workflow into a custom browser shell.

## Why this is separate from Herm and Workspace

HUDUI is a web app/HUD UI. Herm is terminal/TUI oriented. Hermes Workspace is a separate web app/workspace UI. They have different jobs, different likely sizing needs inside Wave, and different implementation lifecycles.

Keeping HUDUI as a standalone widget avoids a mega-widget that must decide whether it is a terminal launcher, workspace UI, or HUD. It also makes the planned implementation easier to test and install independently.

A launcher or meta-widget could be added later to open all Hermes-related surfaces from one place. That should be additive. It should not collapse the standalone Herm terminal, Hermes Workspace, and Hermes HUDUI widget subprojects.

## Feasibility notes

* Wave supports URL-based web widgets with `view: "web"`, `url`, and `pinnedurl`.
* HUDUI may fit best as a compact pane if the upstream UI is designed for dashboard or status use.
* A local backend may be needed only if the source project requires local serving.
* This plan does not assume browser automation, extension support, or unsupported Wave webview APIs.
* No port is reserved yet.

## Implementation questions

* Does Hermes HUDUI ship its own web server, or does it need a small local wrapper?
* What is the intended screen size or layout density for the HUD surface?
* What health check or readiness signal does the source project document?
