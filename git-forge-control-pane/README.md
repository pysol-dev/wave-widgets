# Git Forge Control Pane

## Purpose

This directory is a planning placeholder for a Wave Terminal widget that gives a persistent, environment aware control pane for local Git work and remote forge work across GitHub and Forgejo.

The user problem is repeated browser sign in inside Wave. A better answer is not to turn Wave into an authentication store. The control pane should keep authentication in the existing command line tools and credential stores, then show useful repository and forge state through a local backend.

## Feasibility Summary

The widget is feasible as a local backend with a Wave web view frontend. Wave can show a local web app cleanly, while the backend can run trusted local commands and inspect local repositories. That shape matches the problem better than a pure browser based widget.

A pure web widget is weak for this use case because it runs in a browser shaped environment. It can render a nice dashboard, but it doesn't naturally know which directory is active, which Git remotes exist, which credential helpers are configured, or which forge command line sessions are already authenticated. It would also push the design toward browser OAuth flows and repeated sign ins, which is the behavior the user wants to avoid.

A local backend is stronger because it can read repository state from disk, run read only Git commands, call forge CLIs such as `gh`, `tea`, and `fj`, and respect the host's existing auth model. The web view can stay thin. It presents state and actions, while the backend owns environment discovery and controlled command execution.

## Auth Direction

Persistent auth should likely live in `gh`, `tea`, `fj`, and the operating system or XDG credential storage they already use. The Wave widget should not become the source of truth for tokens, cookies, or long lived credentials.

This keeps the widget safer and simpler. It can ask the backend whether a tool is authenticated, show a clear status such as `GitHub: signed in through gh`, and offer setup guidance when a tool is missing or logged out. It should not store personal access tokens in local widget config, browser storage, or Wave widget metadata.

The widget can still support sign in workflows by pointing users to the correct CLI command in a normal terminal, for example `gh auth login`, `tea login`, or the matching `fj` setup command. Once those tools are authenticated, the widget can use their existing sessions.

## Local Git Concerns

Local repository work is filesystem and working tree centered. The important questions are different from remote forge questions.

Local Git concerns include:

1. Which repository am I in?
2. Which branch is checked out?
3. What changed in the working tree?
4. Which files are staged, unstaged, untracked, or conflicted?
5. What is ahead or behind the upstream branch?
6. Are there stashes, worktrees, submodules, hooks, or merge states that affect action safety?
7. Which remote maps to which forge host?

The best inspiration for this side is LazyGit and GitUI. Both treat local Git as an interactive command surface, not just a status page. They put branches, files, commits, stashes, and remotes close together. They also make risky actions visible and deliberate.

For the Wave widget, the first local Git version should be read heavy. It can show state, copy commands, and open focused views before it attempts write actions such as staging, committing, rebasing, or deleting branches.

## Remote Forge Concerns

Remote forge work is host, account, and collaboration centered. It cares less about the working tree and more about network resources.

Remote forge concerns include:

1. Which forge owns the active remote?
2. Which account is authenticated for that forge?
3. Which pull requests, issues, checks, reviews, and releases relate to the current repo?
4. Which notifications or assigned reviews need attention?
5. What CI status blocks the current branch?
6. Does the local branch have a matching pull request or merge request?
7. Does the remote host use GitHub style APIs, Forgejo APIs, or a CLI specific model?

The best inspiration for this side is `gh-dash`, `tea`, and `fj`.

`gh-dash` is useful as a model for GitHub focused pull request, issue, and notification dashboards. It shows how much value comes from filtering, keyboard friendly navigation, and opinionated summaries.

`tea` is useful because it targets Gitea and Forgejo style forges and already carries the account and host configuration model for those ecosystems.

`fj` is relevant as a Forgejo specific CLI direction. The widget should treat it as a preferred Forgejo foundation where available, while keeping `tea` as a practical fallback if it is already installed and authenticated.

## Recommended Architecture

The recommended shape is a local service plus a Wave web widget.

1. Wave opens a web view pointed at `http://127.0.0.1:<port>`.
2. A LaunchAgent keeps a small local backend available.
3. The backend exposes narrow JSON endpoints for repository status, detected remotes, forge auth status, pull requests, issues, checks, and safe actions.
4. The backend talks to local Git and forge CLIs. It doesn't store forge tokens itself.
5. The frontend renders a control pane with tabs or columns for local Git, current branch, pull request, checks, and forge inbox.
6. Write actions start as copyable commands or explicit backend actions with confirmation.

The backend should bind to `127.0.0.1` only. It should assume local trust, but still keep the API small. Dangerous actions should be explicit and visible in the UI.

The control pane should separate discovery from action. Discovery is safe to refresh often. Actions should require a deliberate click and should show the command or effect before running.

## Environment Model

The widget should understand multiple environments without hard coding personal paths or hostnames.

Useful inputs include:

1. A configured list of workspace roots, using placeholders such as `$HOME/src` in examples.
2. The current repository path, when Wave or the user provides one.
3. Git remotes from `git remote -v`.
4. Forge host mappings from `gh`, `tea`, and `fj` config.
5. Credential state reported by the CLIs, not by direct token inspection.

The widget should avoid storing sensitive host details in examples. Documentation and templates should use placeholders such as `<forge-host>`, `<owner>`, `<repo>`, and `$HOME/src/<project>`.

## MVP

The MVP should prove that a persistent local control pane removes repeated browser sign ins and gives useful repo context.

MVP capabilities:

1. Detect one selected local repository.
2. Show branch, upstream, ahead or behind count, working tree summary, and merge or rebase state.
3. Detect remotes and classify GitHub versus Forgejo style hosts.
4. Show auth status for `gh`, `tea`, and `fj` without reading or storing tokens.
5. For GitHub remotes, show the current branch pull request and checks when `gh` is authenticated.
6. For Forgejo remotes, show repository, issue, or pull request summaries through `fj` or `tea` when available.
7. Provide copyable commands for login, refresh, checkout, open pull request, and inspect checks.
8. Keep all example paths, hostnames, owners, and repos generic.

MVP non goals:

1. No browser extension support.
2. No Wave specific hidden auth assumptions.
3. No token storage in the frontend.
4. No root repository documentation changes.
5. No destructive Git actions.

## Design Direction

The UI should feel like a control pane, not a full replacement for LazyGit or a forge website.

Strong first views:

1. Current repo summary.
2. Working tree status.
3. Current branch and upstream state.
4. Pull request or merge request status.
5. Checks and review state.
6. Forge auth health.

The local Git column should answer, `What is happening on disk?`

The remote forge column should answer, `What is happening on the server?`

The action area should answer, `What can I safely do next?`

## Tool Inspiration And Foundations

LazyGit is the strongest model for local Git workflows. Its value is the dense relationship between file changes, branch history, stashes, remotes, and commits.

GitUI is another strong local Git reference. It is fast, keyboard friendly, and focused on common Git actions without requiring a browser.

`gh-dash` is the best GitHub dashboard inspiration. It focuses on pull requests, issues, reviews, and notifications instead of trying to expose every GitHub feature.

`gh` should be the default GitHub foundation because it already handles GitHub auth, host config, API calls, and user expectations.

`tea` is a practical Gitea and Forgejo foundation where installed. It can provide host aware forge access without custom token handling in the widget.

`fj` should be evaluated as the preferred Forgejo specific foundation where available. It may reduce mismatch with Forgejo behavior compared with generic Gitea tooling.

## Open Questions

1. How should Wave or the user choose the active repository when multiple Wave panes or workspace roots exist?
2. Should the backend support multiple repos at once, or only the active repo for the first version?
3. Which Forgejo CLI should be treated as the primary path on this machine, `fj` or `tea`?
4. What is the safest first write action, if any, after the read only MVP?
5. Should the widget show a forge inbox across accounts, or stay scoped to the current repo?
6. How should errors from missing CLIs, expired sessions, or unsupported forge hosts be presented without exposing sensitive paths or hosts?
7. Does the final widget need a native companion command for opening the control pane with an explicit repo path?

## Planning Conclusion

The best design is a local backend with a Wave web view frontend. That gives Wave a persistent, environment aware control pane without pretending that the browser view can own local Git context or long lived forge authentication.

Local Git state and remote forge state should stay separate in the model. Git answers what changed on disk. GitHub and Forgejo answer what changed on the server. The widget becomes useful by joining those views around the current repository and branch.

Authentication should remain with `gh`, `tea`, `fj`, and the host credential storage they already use, including OS and XDG backed stores. The widget should report auth state and guide setup, not store secrets.
