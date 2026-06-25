# Herm Terminal Widget

Status: planned. This directory is intentionally README-only until implementation starts.

## Purpose

This subproject captures a Wave Terminal widget direction for Herm as a terminal or TUI surface. Herm is the command-line oriented surface in this set, so the natural Wave shape is a `view: "term"` widget that opens a terminal pane around the Herm command or TUI entrypoint.

The goal is not to replace the official Herm terminal pane. The goal is to package a repeatable Wave sidebar entry for people who want Herm available as a named workspace surface alongside other Wave panes.

## Proposed Wave shape

Use a terminal widget, not a web widget.

```json
{
  "herm-terminal": {
    "icon": "terminal",
    "label": "Herm",
    "blockdef": {
      "meta": {
        "view": "term"
      }
    }
  }
}
```

The exact command should come from the Herm project documentation or local install method at implementation time. This README does not claim a specific binary name, flags, environment variables, or session protocol.

## Coexistence with the official Herm terminal pane

This widget should coexist with the official Herm terminal pane by staying thin:

* It can provide a stable Wave sidebar entry.
* It can open Herm in a predictable terminal block.
* It should not wrap, proxy, or reinterpret Herm behavior unless the Herm source project documents that integration path.

Keeping this as a terminal widget preserves Herm's native interaction model. Users who already prefer the official pane can keep using it directly, while this subproject can focus on Wave-specific packaging.

## Why this is separate from the Hermes widgets

Herm is terminal/TUI oriented. `hermes-workspace-widget` and `hermes-hudui-widget` are browser/web app surfaces. Combining them into one widget would blur terminal and web lifecycle concerns, make Wave configuration harder to reason about, and risk hiding the official Herm terminal experience behind a custom dashboard.

A launcher or meta-widget could be added later to open this widget and the Hermes web widgets from one place. That should be a separate project. These surfaces should remain standalone widget subprojects.

## Feasibility notes

* Wave supports terminal-backed widgets through `view: "term"`.
* This direction does not need a local HTTP server unless a later, documented Herm integration requires one.
* No browser automation, webview scripting, or extension behavior is assumed.
* No port is reserved yet.

## Implementation questions

* What Herm command should the Wave terminal block run?
* Should the widget open in a plain shell first, or directly run the Herm TUI?
* Does Herm document any Wave-specific or terminal-embedding guidance that should be reflected in the install script?
