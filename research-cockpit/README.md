# Research Cockpit Widget Notes

## Purpose

The research cockpit is a Wave Terminal widget plan for human guided deep research. Its first version should give a researcher one place to open sources, track questions, collect notes, coordinate worker panes, and keep the research plan visible without turning Wave into a full browser automation stack or a replacement agent runtime.

The intended use case is exploratory work where context matters more than a single page:

- source pages and docs in nearby web panes
- an agent or shell pane for synthesis
- a notes or queue view for claims, links, and follow ups
- explicit controls for opening related panes in a predictable layout
- persistent session state that survives beyond the live agent context
- verification checkpoints before claims are accepted into the final synthesis

The planning model is inspired by Anthropic's orchestrator worker pattern for multi agent research: one coordinating surface keeps the research plan, routes work to bounded specialist workers, and pulls results back through review. The cockpit should make that pattern visible and controllable in Wave while relying on Hermes backed browser, research, and orchestration primitives where they already exist.

## Current Repository State

This directory now contains a real v1 scaffold:

- `README.md`, this implementation note and planning reference
- `server.py`, the local backend
- `config.template.json`, user-owned workflow and profile template data
- `install.sh`, the local installer and Wave widget registration script
- `SETUP.md`, widget-local setup and API notes
- `.gitignore`, runtime and local-state ignore rules
- `static/index.html`, `static/app.js`, and `static/styles.css`, the Wave web UI

The current committed scaffold is intentionally small, local, and inspectable. It proves the control-plane shape without claiming direct Hermes APIs, deterministic adjacency helpers, or browser automation.

## Current V1 Boundary

Implemented now:

- a local backend bound to `127.0.0.1`
- a direct Wave `view: "web"` widget registration path through `install.sh`
- persisted local session state in `state/session.json`
- a static cockpit UI for research brief, phases, source queue, worker queue, notes, and claim verification state
- source URL validation and same-pane source opening through `/open/source/<id>`
- copyable Wave commands such as `wsh web open ...` without requiring the LaunchAgent to call `wsh`
- modular workflow/profile template data in `config.template.json`
- Anthropic-style orchestrator-worker workflow guidance and Hermes-aware role language

Still deferred:

- deterministic adjacent placement from `/deep-research`
- a helper that uses `$WAVETERM_BLOCKID` and Wave split actions
- direct Hermes API calls from widget code
- browser automation, click control, form filling, extension loading, or JavaScript execution against Wave web panes
- private prompts, fixed swarm identities, or hard-coded model/provider choices

This v1 boundary is intentional. The widget is a visible control layer and local state surface, not a replacement runtime.

## Install Flow

The current scaffold can be installed locally through `install.sh`.

At a high level it:

- copies `config.template.json` to `config.json` if needed
- creates the local `state/` directory
- generates and loads a LaunchAgent named `wave.widgets.research-cockpit`
- starts the backend on `http://127.0.0.1:8792`
- adds a `Research` direct web widget entry to `/Users/<user>/.config/waveterm/widgets.json`

The detailed commands and troubleshooting notes live in `SETUP.md` and should stay there so the root docs remain concise.

## Why This Should Be Standalone

This repository uses one top level directory per widget. The research cockpit should follow that convention because it has its own product surface, helper needs, and launch behavior.

It should not be folded into another dashboard because its hard part is layout orchestration, not just rendering a page. The widget needs to know about research sessions, source queues, adjacent panes, and possibly Wave block targeting. Those concerns are separate from port maps, model dashboards, and app launchers.

Keeping it standalone also lets the first implementation stay small. The MVP can ship as a simple local web widget with a narrow helper. Later versions can add richer Wave integration without coupling other widgets to experimental internals.

## Current Feasibility Conclusion

Wave is a good fit for a research cockpit as an orchestration and visibility surface. It is not, by itself, a full browser automation platform.

Key conclusion: same tab spawning is feasible, and deterministic adjacency is optional for v1. The stock widget bar and normal `wsh` launch paths do not currently prove that a new terminal or web block appears adjacent to the originating widget. Internal Wave create block APIs do support explicit placement and split actions, so deterministic adjacency remains a later helper or integration concern rather than a requirement for the first planning milestone.

For a slash command such as `/deep-research`, launching a paired cockpit layout would need one of these approaches:

- a helper that reads `$WAVETERM_BLOCKID` from the calling block and requests split actions around that block
- a patched Wave launch flow that passes the source block ID into block creation
- a custom integration that uses internal create block APIs rather than relying only on stock widget bar behavior

Without that targeting path, the command can open a research URL or widget in the same workspace flow, but it should not promise the cockpit lands next to the initiating pane.

## Research Workflow Model

The cockpit should model research as a phase based workflow rather than as a chat transcript. A useful session starts broad, narrows through evidence, then verifies the final answer before publishing or handing it off.

Recommended phases:

- frame the question, scope, constraints, and expected output
- survey broadly across source types, terms, and competing explanations
- split into parallel specialist passes, such as source discovery, claim extraction, contradiction hunting, citation checking, and synthesis
- narrow around the strongest evidence and unresolved questions
- verify citations, dates, quotes, and source quality before accepting findings
- preserve the plan, sources, intermediate notes, and rejected claims outside the live agent context
- produce a final synthesis with traceable claims and open questions

This follows the Anthropic orchestrator worker shape without hard coding a swarm runtime into the widget. The cockpit is the control layer. Hermes backed tools and user selected workers remain the execution layer.

## Phased Swarm Pipeline

The planning target is a bounded research pipeline, not agent personality sprawl. A session can still feel like a swarm, but each worker should have a clear job, input, output, and stop condition.

Pipeline stages:

- Orchestrate: maintain the research brief, split the question into tasks, and decide what evidence is still missing.
- Explore: run broad source discovery across search, docs, pages, local notes, and user supplied links.
- Specialize: assign narrow passes to workers with roles such as source finder, domain reader, skeptic, citation checker, and summarizer.
- Consolidate: merge findings into a shared state file or local session record instead of relying on one live context window.
- Verify: check citations, source freshness, quoted text, contradictions, and whether the answer overstates the evidence.
- Synthesize: draft the result only after verification gates have passed or open gaps have been called out.

The cockpit should expose these phases as planning state and operator controls. It should not hide them inside an opaque autonomous run.

## Hermes Backed Role Model

Hermes already provides browser, research, and orchestration primitives. The cockpit should coordinate those capabilities rather than replace them.

Planning roles:

- Orchestrator: keeps the research plan, phase status, worker queue, open questions, and final handoff shape.
- Browser worker: opens, reads, screenshots, or inspects sources through existing browser capable primitives when available.
- Research worker: searches, reads, extracts candidate claims, and records source metadata.
- Skeptic worker: looks for contradictions, weak sources, missing context, and unsupported jumps.
- Citation worker: checks whether each final claim has a source, a stable citation, and enough context to be audited.
- Synthesis worker: writes the final answer from accepted evidence and marks remaining uncertainty.

These are process roles, not permanent agent personalities. Future custom profiles should be user owned configuration, prompts, or templates. The repository should not bake in a fixed cast of agents or a closed swarm design.

## What Wave Can Do Natively

Native Wave behavior is enough for a useful first cockpit if the widget accepts manual or semi manual layout control.

Wave can natively support:

- web widgets that show a fixed local or remote URL
- web panes for docs, search results, dashboards, and local preview pages
- `wsh web open` for opening a URL in a web block
- `wsh setmeta` style URL retargeting for an existing web block
- screenshots of web panes through Wave AI related tooling
- persistent pane metadata such as URL and related web settings
- multi block terminal and web layouts that are useful for side by side research

These capabilities make Wave strong for human in the loop research, reading, comparing, note taking, and agent assisted synthesis.

## What Wave Does Not Currently Guarantee Natively

The researched evidence does not support claiming native deterministic adjacency from the stock widget bar or normal `wsh` launch alone.

Wave also should not be described as natively providing:

- full browser automation comparable to Playwright or Puppeteer
- reliable click, type, form fill, or arbitrary JavaScript evaluation against adjacent web panes through supported public interfaces
- browser extension loading for web panes
- durable browser profile semantics across restarts
- automatic click to source reference workflows like a dedicated browser developer tool bridge

The cockpit can coordinate research around web panes, but it should not promise autonomous browser control unless an external automation tool or custom bridge is added.

## What Requires A Custom Backend Or Helper

Deterministic adjacent spawning is a custom requirement only if the user wants the first version to guarantee exact layout placement. It is not required for a useful v1.

A helper is needed when the widget or slash command must create blocks relative to the caller. The helper should receive or discover the source block ID, then request a split layout using Wave internals that understand placement. `$WAVETERM_BLOCKID` is the key environment variable for commands launched from an existing Wave block, but it only helps if the launch flow passes it into a helper that can target split actions.

A custom backend or helper would also be useful for:

- storing research sessions and source queues
- normalizing URLs and titles for saved sources
- exposing local actions for opening sources in Wave panes
- coordinating notes, summaries, and agent prompts
- preserving the active research plan and worker state outside the live context window
- recording citations, verification status, rejected claims, and unresolved questions
- bridging to external browser automation if a future workflow needs clicks or form filling

If a backend is added later, it should bind locally, avoid secrets in the repository, and document any user data location with placeholders. If persisted user data is needed, provide a template config rather than committing real config.

## Recommended Architecture

Use a local web widget as the primary UI and a small local helper for Wave aware actions.

Recommended shape:

- `widgets.json` entry with `view: "web"`, `url`, and `pinnedurl` pointing at the local cockpit UI
- local static UI for the research queue, phase status, session outline, open questions, worker queue, verification state, and action buttons
- optional local backend for session state and Wave placement actions
- optional LaunchAgent so the backend is already running before the widget opens
- helper path for creating adjacent blocks when a source block ID is supplied

The widget should avoid a terminal block that runs `wsh web open` as its main launch mechanism. A direct web widget is the safer Wave pattern for local dashboards, and it avoids depending on Wave managed shell authentication in a context where it may not exist.

Example PII safe paths for a future implementation:

- widget project: `/Users/<user>/dev/wave-widgets/research-cockpit/`
- local service root: `/Users/<user>/research-cockpit/` if the runtime app needs to live outside the repository
- Wave widget config: `/Users/<user>/.config/waveterm/widgets.json`
- LaunchAgent: `/Users/<user>/Library/LaunchAgents/wave.widgets.research-cockpit.plist`

## MVP

The MVP should prove the cockpit is useful before depending on deep Wave internals.

Minimum useful version:

- a local web widget showing a research session title, current question, phase status, source queue, worker queue, and notes area
- buttons or copyable commands for opening sources in Wave web panes
- clear display of what can be opened manually versus what can be placed deterministically
- a visible research plan that records broad survey, narrow follow up, verification, and synthesis stages
- a citation and verification checklist for claims that will appear in the final synthesis
- README documentation for the launch path, limits, future adjacency helper, and user owned profile model

If the MVP includes a helper, keep the first helper narrow:

- accept a source block ID
- accept a URL or command label
- create the requested adjacent split through the supported internal path available in the target Wave version
- return clear success or failure state to the cockpit UI

Do not add browser automation to the MVP. Treat that as a separate later layer.

## Evaluation And Verification Gates

Deep research fails when broad search becomes shallow summary, citations drift away from claims, or the agent forgets earlier constraints. The cockpit should make those failures visible before synthesis.

Required planning gates:

- Brief gate: the question, scope, exclusions, and expected output are explicit before workers start.
- Breadth gate: the session records search terms, source types, and at least one competing angle before narrowing.
- Evidence gate: candidate claims are tied to source links, notes, and citation status.
- Skeptic gate: contradictions, missing evidence, weak sources, and stale information are reviewed before writing.
- Citation gate: final claims are checked against their cited source and marked accepted, rejected, or unresolved.
- State gate: the plan, worker outputs, source queue, and unresolved questions are persisted outside the live context.

The cockpit should prefer visible review state over silent confidence scores. A claim can be useful, rejected, or unresolved, but it should not disappear just because the live context moved on.

## Extensibility Stance

Future swarm orchestration should stay user owned.

The widget may offer templates for phases, roles, and worker instructions, but custom orchestration plans and agent profiles should live in user editable config or local session data. The repository should avoid hard coded model choices, fixed agent identities, private prompts, or a single required research method.

Good extension points:

- user editable phase templates
- user editable worker role definitions with bounded inputs and outputs
- saved research session state and source queues
- optional bridges to Hermes backed tools already present in the user's environment
- optional Wave placement helper when exact layout matters

The default posture should be small, inspectable, and reversible. The cockpit coordinates research, records state, and surfaces verification. It does not own the user's agents.

## Open Questions

- Which internal create block API should the helper target for the current Wave version?
- Can the helper call that API safely from a normal local backend, or does it need to run inside a Wave aware command context?
- How should `/deep-research` pass `$WAVETERM_BLOCKID` into the helper without depending on fragile shell state?
- Should deterministic layout wait until after the first cockpit proves the research workflow?
- What minimal persistent state format is enough for the MVP plan, sources, worker outputs, citations, and unresolved questions?
- What validation is needed to avoid opening untrusted commands while still allowing user supplied research URLs?
- How should user owned worker profiles be represented without baking a fixed swarm into the repository?
- Which Hermes backed capabilities should the cockpit call directly, and which should stay as user launched worker panes?

## Planning Notes

Build this as a Wave orchestration widget, not as a hidden browser automation system or a replacement runtime. The strongest first version helps a human and Hermes backed workers stay organized in Wave, keeps the broad then narrow research plan visible, preserves state outside the live context, and forces citations through verification before synthesis. Deterministic adjacency is useful, but it is optional for v1 because same tab spawning and manual layout are enough to validate the research cockpit model.
