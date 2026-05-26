# Wave web panes, widgets, and agent/browser workflows

This document answers four questions about Wave Terminal's web panes/widgets using first-party docs, Wave source code, and a small amount of external reference material where Wave itself stops short.

## Scope and method

- **Primary sources**: Wave docs and the Wave source repo.
- **Secondary sources**: Playwright source for comparison on persistent browser profiles and extension loading.
- **Goal**: describe what Wave can do **natively**, what it can do with a **custom widget/backend**, and what requires **external browser automation**.

## Short answers

1. **Can a terminal-pane agent natively operate an adjacent web pane like a real browser automation session?**
   - **Partially**. Natively, Wave can open/navigate web panes, update their URL, take screenshots, and expose a hidden CSS-selector HTML extraction path.
   - **Not fully**. There is no first-party evidence of native click/type/eval/form-fill/wallet-signing/browser-extension automation comparable to Playwright/Puppeteer.
   - **“Total stealth mode”** is **not** a native Wave capability. Wave exposes UA switching and storage partitioning/clearing, but not a complete anti-detection or extension-backed browser automation stack.

2. **Can adjacent terminal panes and web panes behave like cmux/Windsurf in-IDE preview?**
   - **Yes, at the preview/navigation level**: local dev servers can be shown in a web pane, and agents/scripts can retarget those panes by URL.
   - **No, not natively at the DOM workflow level**: no first-party adjacent-pane bridge was found for click-to-reference, DOM event forwarding, or arbitrary browser automation.
   - **A richer custom widget is plausible**, but it would need to be implemented as a custom Wave app/widget or backed by external tooling.

3. **How persistent are Wave web sessions? Do they survive app restarts? Are extensions supported?**
   - **Wave persists pane metadata** like URL and related web settings.
   - **Wave does not document durable restoration of live web page state**; official docs explicitly say webpage progress can be lost on window close.
   - **No first-party browser-extension support was found**.

4. **How powerful can Wave widgets be?**
   - Very powerful as **URL-based web widgets**, **terminal-backed widgets**, or **custom app-style widgets**.
   - The ceiling is high for dashboards, local app launchers, control panels, observability tools, research cockpits, and workflow frontends.
   - The ceiling is much lower for **arbitrary browser automation** unless external tools are added.

---

## 1) Native agentic browser sessions in Wave: what exists vs what does not

### What exists natively

#### A. Web panes are real embedded Chromium webviews

Wave's web pane is implemented with Electron `<webview>` and supports URL loading, a preload script, optional partition selection, and user-agent override.

Sources:
- Wave source: `frontend/app/view/webview/webview.tsx` shows the actual `<webview>` element with `src`, `preload`, `partition`, and `useragent` ([source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/frontend/app/view/webview/webview.tsx#L1107-L1122)).

#### B. Terminal-side control exists at the URL/navigation level

Wave's CLI can create/open a web block and navigate it to a URL.

Sources:
- `wsh web open` is documented in Wave docs ([docs](https://docs.waveterm.dev/wsh), [source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/docs/docs/wsh.mdx#L81-L97)).
- `wsh web open [url] [-m] [-r blockid]` is documented in the CLI reference ([source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/docs/docs/wsh-reference.mdx#L424-L456)).
- `wsh setmeta -b [blockid] url=...` updates a web block instantly ([source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/docs/docs/wsh-reference.mdx#L104-L122)).

#### C. Wave AI exposes browser-adjacent tools, but they are limited

Wave AI documents:
- **Navigate Web**: changes URLs in web browser widgets.
- **Screenshot**: captures widget/browser visuals.
- **Web content extraction**: not yet first-class; docs explicitly say “currently screenshots only.”

Sources:
- Wave AI docs ([docs](https://docs.waveterm.dev/waveai), [source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/docs/docs/waveai.mdx#L67-L72), [source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/docs/docs/waveai.mdx#L101-L108)).
- Local Wave source investigation found `web_navigate` and screenshot tools in `pkg/aiusechat/tools_web.go`, `pkg/aiusechat/tools_screenshot.go`, and `pkg/aiusechat/tools.go`.

#### D. There is a hidden selector-based extraction path

Local Wave source investigation found a hidden `wsh web get` path that can resolve a CSS selector and return `innerHTML` / `outerHTML` from a web pane via Electron IPC.

Local source paths identified during research:
- `cmd/wsh/cmd/wshcmd-web.go`
- `emain/emain-web.ts`
- `emain/emain-wsh.ts`
- `emain/preload.ts`

This is important: **it is evidence of limited introspection**, but **not** of full automation.

### What does not exist natively

No first-party source was found for:
- click automation
- keyboard typing / form filling
- arbitrary JS evaluation against the page via supported CLI/AI interface
- wallet extension injection/signing flows
- anti-bot or stealth automation stack
- prolonged autonomous browser workflows comparable to Playwright/Puppeteer/Selenium

### Bottom line for question (1)

**Definitive answer**: Wave supports **adjacent browser viewing and limited navigation/introspection**, but **not native full browser automation**. A coding agent in a terminal pane can point, refresh, inspect visually, and in some cases extract selector HTML from an adjacent web pane. That is **not enough** to call it a native autonomous agentic browser stack.

### About “total stealth mode” / operating social accounts

Technically, Wave provides:
- user-agent switching
- webview partitions
- storage clearing

Technically, Wave does **not** provide evidence of:
- extension-backed identity/persistent profile management
- anti-detection instrumentation
- Playwright-style persistent contexts
- automated login/session orchestration

So the sourced answer is: **no, not natively**.

Supporting sources:
- user-agent controls in `webview.tsx` ([source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/frontend/app/view/webview/webview.tsx#L644-L685))
- web partition support in `webview.tsx` and meta constants (`web:partition`) ([source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/frontend/app/view/webview/webview.tsx#L855-L858))

---

## 2) Adjacent terminal + web pane editing, previews, dApps, wallets, click-to-reference

### Native preview behavior: yes

Wave can absolutely function as an in-terminal/browser preview surface:
- run `npm run dev` in one pane
- open `http://localhost:3000` in another web pane
- retarget or refresh from the terminal

Sources:
- Wave docs show exactly this localhost workflow ([source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/docs/docs/wsh.mdx#L103-L118)).

### Native DOM/editing coupling: no

No first-party source was found for a built-in adjacent-pane bridge like:
- “click an element in the preview and send a structured reference to the coding agent”
- live element picking and code mapping
- DOM-driven edit suggestions
- preview element → source location mapping

The closest native features are:
- URL updates
- screenshot capture
- hidden selector HTML extraction

That is weaker than Windsurf “In-IDE Preview” or a bespoke browser/devtool bridge.

### Can this be turned into a widget with richer capabilities?

**Yes, probably — but not as a pure stock web widget.**

There are three levels here:

#### Level 1: stock web widget

What it can do:
- show any URL
- act as a browser surface for a dev server / app / dashboard
- be navigated by `wsh` or Wave AI

Source:
- custom web widget docs ([docs](https://docs.waveterm.dev/customwidgets), [source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/docs/docs/customwidgets.mdx#L261-L288)).

#### Level 2: local backend + custom web widget

This is the realistic path for:
- click-to-reference
- emitting selected DOM data to a terminal/agent channel
- dApp testing dashboards
- research monitors
- specialized browser-adjacent tooling

This works because Wave widgets can be local apps and local HTTP surfaces, not just fixed URLs.

#### Level 3: custom Wave app / Tsunami / WaveApp path

Local source research found that Wave's richer app/widget framework exposes:
- app events
- forms/files/refs
- data/config APIs
- optional AI tool integration for widgets

Local source paths identified during research:
- `frontend/app/view/tsunami/tsunami.tsx`
- `tsunami/vdom/vdom_types.go`
- `pkg/aiusechat/tools_tsunami.go`

This is the strongest path for building something like:
- a dApp test cockpit
- a wallet flow test dashboard
- click-to-reference tooling
- a multi-pane research assistant UI

### Wallet signing / web3 / crypto dApps

#### What is realistic natively in Wave

- viewing and using a dApp in a web pane
- testing WalletConnect-style external wallet flows if the site supports them
- testing app rendering, navigation, and non-extension flows

#### What is not evidenced natively

- running MetaMask-style extension wallets inside Wave's browser surface
- loading Chrome extensions into the Wave webview

Wave does expose a Chromium webview, but no first-party extension loading feature was found. The only `chrome-extension://` evidence found in source is a narrow allowlist for the built-in PDF viewer URL, not general extension support.

Source:
- `emain-util.ts` PDF-viewer allowlist ([source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/emain/emain-util.ts#L148-L157)).

### Bottom line for question (2)

- **Preview and adjacent browsing? Yes.**
- **Native cmux/Windsurf-grade browser→editor coupling? No.**
- **Powerful custom widget/tooling around this? Yes, but it would need additional bridge code or a richer Wave app/widget architecture.**
- **Extension-wallet testing? Not natively evidenced. External browser automation is the realistic answer there.**

---

## 3) Persistence: cookies, sessions, restarts, and browser extensions

### What Wave persists

Wave persists **web pane metadata** such as current URL and related per-block web settings.

Local and first-party evidence:
- `webview.tsx` updates block meta when navigation changes.
- local research found persistence plumbing through `pkg/wstore/wstore.go`, `pkg/wstore/wstore_dbops.go`, and `db/migrations-wstore/000001_init.up.sql`.

### What Wave does not guarantee

Wave's official docs explicitly state that webpage progress can be lost on close.

Source:
- Workspaces docs ([docs](https://docs.waveterm.dev/workspaces), [source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/docs/docs/workspaces.mdx#L37-L69)).

Wave also says webview state is persisted across **tab changes**, which is weaker than “full browser session/profile survives app restarts with everything intact.”

Source:
- Release notes ([docs](https://docs.waveterm.dev/releasenotes), [source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/docs/docs/releasenotes.mdx#L553-L558)).

### Cookie/storage handling

Wave exposes “Clear Cookies and Storage (All Web Widgets)” in the UI, and the Electron-side implementation calls `wc.session.clearStorageData()`.

Sources:
- menu action in `webview.tsx` ([source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/frontend/app/view/webview/webview.tsx#L706-L748))
- storage clearing in `emain-ipc.ts` ([source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/emain/emain-ipc.ts#L383-L392))

### Partition support

Wave exposes a `web:partition` setting in metadata and wires that into the Electron webview `partition` attribute.

Source:
- `webview.tsx` partition plumbing ([source](https://github.com/wavetermdev/waveterm/blob/021db67ee7af1771d0b4b9bf09c098fa7747e5cd/frontend/app/view/webview/webview.tsx#L855-L858))

### Browser extensions

No first-party docs or source evidence were found for:
- installing Chrome extensions
- loading browser extensions for a web pane
- password-manager extension support
- wallet-extension support

So the definitive sourced answer is:

- **persistent pane metadata: yes**
- **tab-change state persistence: yes**
- **fully durable browser-profile semantics across restarts: not documented, and official docs warn that webpage progress may be lost**
- **browser extension support: no first-party evidence found**

### Practical answer for “sign into GitHub every time”

Based on Wave's own docs/source, you should **not** assume Wave behaves like a fully managed Chrome profile with extension support and durable session restoration guarantees. If persistent authenticated browser state is critical, an external browser profile is the safer assumption.

---

## 4) How to think about Wave widgets: the real ceiling, with concrete examples

The useful framing is that Wave widgets come in three broad buckets:

1. **Web widgets**: browser surfaces for any URL or local app
2. **Terminal-backed widgets**: shell/CLI command surfaces
3. **App-style custom widgets**: richer local apps/widgets with their own backend and UI

### A. Extremely practical widgets you can build today

#### 1. Local dev preview launcher
- open your dev server
- switch between staging/localhost routes
- capture screenshots
- expose quick links for docs, Storybook, admin panels

Why it fits:
- native web widgets + `wsh web open` + `setmeta`

#### 2. Research cockpit
- search tabs
- docs pages
- competitor dashboards
- issue trackers
- local notes/agent output in neighboring panes

Why it fits:
- web panes plus Wave's multi-block layouts are a strong human-in-the-loop research setup

#### 3. Incident/debug dashboard
- Grafana
- Kibana
- status pages
- local logs/SSH panes
- action scripts in a terminal pane

Why it fits:
- Wave already excels at mixed terminal + web layouts

#### 4. Workflow control center
- n8n launcher
- Airflow UI launcher
- Temporal visibility UI
- build/deploy dashboards
- API docs + cURL/test panes nearby

Why it fits:
- web widgets are ideal for “UI launchers with operational context next door”

### B. More advanced widgets that are realistic with a local backend

#### 5. DOM selector/reference helper
- user clicks or picks elements in a local preview
- helper widget records selectors / HTML snippets
- sends them to a terminal/agent context panel

Why it fits:
- not native today, but a local backend + custom widget can bridge this

#### 6. Blockchain / dApp test console
- displays chain status, RPC health, wallet test status, contract addresses, explorer links
- launches target dApps in a web pane
- records screenshots and environment info

Why it fits:
- realistic as a control center, but wallet-extension flows likely require an external browser

#### 7. Agent QA dashboard
- list of dev servers
- health checks
- preview URLs
- screenshot status
- “open route in pane N” controls

Why it fits:
- ideal for a local backend + web widget model

### C. Highest-ceiling conceptual widgets

These are the most powerful things I can justify as *plausible* inside Wave's widget model, even if they do not exist yet:

#### 8. Full-stack product cockpit
- one widget for route catalog + screenshot baselines
- one for service health
- one for database migration state
- one for feature flags
- adjacent code/agent panes for fixes

#### 9. Security review cockpit
- app preview
- dependency and secret scan results
- captured screenshots
- links to affected routes/components
- terminal panes for remediation

#### 10. AI-assisted design system lab
- component gallery
- token inspector
- per-breakpoint previews
- generated diffs and screenshots
- direct launch into target routes or stories

### What widgets are **not** the best tool for

Wave widgets are **not** the strongest native answer for:
- heavy browser automation
- extension-dependent workflows
- wallet-extension signing flows
- stealth automation
- Playwright-grade regression testing by themselves

Those are better treated as:
- external browser automation + a Wave dashboard around it, or
- a custom widget that coordinates external automation rather than replacing it

---

## Capability matrix

| Capability | Native Wave | Custom widget/backend | External tooling needed |
|---|---:|---:|---:|
| Open/navigate adjacent browser pane | Yes | Yes | No |
| Localhost preview in adjacent web pane | Yes | Yes | No |
| AI/CLI retarget URL of adjacent pane | Yes | Yes | No |
| Screenshot web pane | Yes | Yes | No |
| Extract page content semantically | Limited | Yes | Often |
| Click/type/fill forms autonomously | No evidence | Possible with added bridge | Yes |
| Click element and send reference to coding agent | No evidence | Plausible | Often |
| dApp front-end preview | Yes | Yes | No |
| Wallet extension signing inside Wave | No evidence | Unlikely | Yes |
| Persistent browser-profile + extensions | No evidence | No clear first-party path | Yes |
| Playwright-grade long autonomous sessions | No | No | Yes |
| “Total stealth” browser automation | No | No | Yes |

---

## Comparison reference: what external tooling gives you that Wave does not

Playwright is a useful baseline because it supports the two big things Wave does not evidence natively:

1. **Persistent browser profiles**
2. **Extension loading**

Sources:
- persistent context example in Playwright source ([source](https://github.com/microsoft/playwright/blob/c758b15077ef8dea7160db266570b3cd664c17b5/tests/library/defaultbrowsercontext-2.spec.ts#L97-L105))
- extension loading example in Playwright source ([source](https://github.com/microsoft/playwright/blob/c758b15077ef8dea7160db266570b3cd664c17b5/tests/library/chromium/extensions.spec.ts#L23-L36))

This is why the right architecture for many advanced workflows is:

- **Wave for orchestration, visibility, previews, dashboards, and adjacent operational context**
- **external browser automation for true autonomous browser control**

---

## Final conclusions

### Q1: Native agentic browser sessions in adjacent Wave panes?
**Limited yes, full no.**

Wave natively supports browser panes, URL navigation, screenshots, and some introspection. It does **not** natively expose a full browser automation stack.

### Q2: Adjacent pane read/edit/manipulate like cmux/Windsurf preview?
**Preview yes, deep coupling no.**

Wave is strong as a preview/orchestration environment. Native DOM-aware adjacent-pane workflows are not evidenced. A custom widget/backend could bridge part of that gap.

### Q3: Persistent browser sessions or extensions?
**Metadata persists; durable browser-profile semantics and extension support are not evidenced.**

Wave explicitly warns that webpage progress can be lost on close. No first-party browser-extension support was found.

### Q4: Under-utilizing widgets?
**Probably yes.**

The best way to think about Wave widgets is not “mini apps inside a terminal,” but “a composable local operating surface for terminals, dashboards, URLs, and custom frontends.”

The highest-value uses are:
- previews
- dashboards
- workflow launchers
- operational cockpits
- agent coordination surfaces
- local backend + UI control panels

The weakest uses are anything that depends on full browser automation or extension-heavy browser identity.
