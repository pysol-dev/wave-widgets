# Unsloth Studio Control

This directory is a planning scaffold for a future Wave Terminal widget that controls and observes a running Unsloth Studio instance. It intentionally contains no implementation files yet.

## Feasibility summary

Unsloth Studio is best treated as a local browser application backed by a local service. The researched shape is a GUI that talks to a backend over HTTP, with live progress and job updates exposed through streaming browser friendly channels such as SSE.

That shape fits Wave well. Wave can open local web apps as native web widgets, so the practical integration is a wrapper and control surface around the running Unsloth backend. The widget should not try to embed Unsloth Studio's internal GUI components or import private frontend code.

No documented embeddable component mode was found. There is no supported evidence of a public React component API, plugin slot, iframe focused embed contract, or standalone GUI module intended for use inside another app. Until Unsloth documents such an API, a wrapper is the safer design.

## What Unsloth Studio is

Unsloth Studio is a local visual interface for working with Unsloth model training workflows. In this planning context, it should be understood as:

- A browser based local app.
- A backend process that owns training control, state, and progress.
- A frontend that consumes backend HTTP endpoints.
- A live status surface that can report progress through server pushed updates.

This makes it closer to a local dashboard plus controller than a library widget that can be embedded directly inside Wave.

## Why Wave should wrap the backend

A Wave widget should sit beside Unsloth Studio rather than inside its private GUI internals.

The wrapper approach has several advantages:

- It respects the current public surface. HTTP and streaming status are normal integration points. Private frontend internals are not.
- It keeps upgrades safer. If Unsloth changes its UI framework or component tree, a wrapper that talks to backend endpoints has less breakage risk.
- It matches Wave's widget model. Wave web widgets work well as local dashboards served from `127.0.0.1`.
- It leaves the native Unsloth Studio UI available. The Wave widget can open, monitor, or link to the running Studio app without replacing it.
- It avoids inventing unsupported APIs. Any direct embed should wait for a documented Unsloth extension or component contract.

The working assumption is that the Wave widget is a control cockpit, not a fork of Unsloth Studio.

## Observable and controllable surfaces

The researched surfaces suggest a practical control widget can focus on:

- Backend health, for example whether the local Unsloth service is reachable.
- Current job state, such as idle, preparing data, training, saving, failed, or completed.
- Progress updates from HTTP polling or SSE style event streams.
- Recent logs or status messages, redacted before display if they contain paths or environment details.
- Safe controls, such as open Studio, refresh status, pause if supported, cancel if supported, and copy launch instructions.
- Configuration visibility, limited to non-secret values and placeholders.

Controls should only be added when there is a confirmed backend endpoint for them. If a capability is only present inside private GUI code, it should remain an open question rather than a widget feature.

## Recommended architecture

The recommended design is a small local Wave web widget with its own adapter server.

```text
Wave web widget
  -> local adapter server on 127.0.0.1
  -> running Unsloth Studio backend
  -> optional link to native Unsloth Studio browser UI
```

The adapter server should:

- Bind to `127.0.0.1` only.
- Read local configuration from a gitignored config file when implementation begins.
- Proxy or normalize only the small set of supported backend status endpoints.
- Subscribe to SSE or similar event streams if they are stable and documented enough.
- Expose a widget friendly health endpoint for Wave.
- Redact local paths, hostnames, tokens, dataset names, and account details from logs before returning data.

The Wave widget UI should:

- Show whether Unsloth Studio is reachable.
- Show current training state and progress.
- Provide a button or link to open the full Studio UI.
- Display recent safe events and errors.
- Keep destructive actions explicit and confirm them in the UI.

## MVP

The first implementation should be intentionally small:

- Detect whether the configured Unsloth backend is running.
- Show backend URL using a placeholder friendly display, such as `http://127.0.0.1:<port>`.
- Show current status and latest progress event when available.
- Provide an `Open Studio` action that opens the full local browser app in Wave or the system browser.
- Provide `Refresh` and `Copy launch command` actions.
- Include clear empty states for backend missing, backend starting, and unsupported endpoint.

The MVP should not include training creation, dataset upload, model export, or process killing unless the matching backend APIs are confirmed and safe.

## Later possibilities

If supported backend APIs exist, later versions could add:

- Job queue overview.
- Training metrics charts.
- GPU or memory status.
- Checkpoint and output artifact summaries.
- Log filtering with PII redaction.
- Safe cancel or pause controls.
- Links from an event to the relevant Studio screen.

These should remain adapter features, not direct imports from Unsloth Studio's frontend.

## Open questions

- What exact local port and launch command does Unsloth Studio use by default?
- Which HTTP endpoints are stable enough to call from a third party control surface?
- Is the live progress channel SSE, WebSocket, long polling, or a mix?
- Are pause, cancel, retry, and resume supported by backend endpoints, or only by GUI internals?
- Does Unsloth document an extension, plugin, or embed API in the future?
- What data in logs needs redaction before display in a public safe widget repo?
- Should the Wave widget open the full Studio UI inside Wave, in the system browser, or offer both?

## Current design stance

Build a Wave native control wrapper around a running Unsloth Studio backend. Do not embed undocumented GUI internals. Treat HTTP and streaming status as the likely integration surface, verify each endpoint during implementation, and keep the first version focused on observability plus safe launch controls.
