# Semanticore component integration

Wave Widgets is an independent monorepo of standalone Wave Terminal applications. Semanticore may check it out as `wave-widgets/` inside a larger workspace without absorbing its history or publishing private coordination data here.

The component owns widget UI/backends/installers and their tests. The coordinator owns shared requirements, cross-component integration pins and review status. GitGov owns implemented governance operations; a Wave widget presents status, plans, diffs and receipts and invokes only an authorized implemented operation. It cannot grant its own command authority.

## Contribution flow

1. Use trusted repository instructions and a bounded issue scope.
2. Work in an isolated branch/checkout and preserve unrelated local changes.
3. Test the affected widget through its real surface; include a failure path when behavior changes.
4. Push a component PR for human review. Keep its SHA and verification linked in the private coordinator; do not copy private issues, plans, hosts or captures into this public repository.
5. Update the coordinator's component pin separately. A clone URL or manifest does not install or restart a widget.

The existing active checkout and LaunchAgent paths stay unchanged when another workspace clone is created. Local unpublished Research Cockpit or Plannotator work must be reconciled explicitly before deployment; a pinned published clone does not contain that work automatically.
