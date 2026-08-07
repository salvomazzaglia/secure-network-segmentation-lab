# Final release checklist — 1.0.0

## Product

- [ ] Synthetic lab generates ~35–40 nodes
- [ ] Six segments with synthetic VLAN labels
- [ ] Classification + confidence explainability
- [ ] Segmentation + reachability policies validate
- [ ] Approval/quarantine simulation banners present
- [ ] 3D + non-3D inspection paths
- [ ] REST + WebSocket on 127.0.0.1

## Privacy / security

- [ ] `scripts/validate-repository.py` passes
- [ ] No RFC1918 in tracked fixtures
- [ ] MACs are `02:` in examples/synthetic
- [ ] No secrets, PCAPs, real screenshots
- [ ] SECURITY.md and threat model published
- [ ] security-audit-v1.0.0.md completed post-audit

## Quality

- [ ] Backend ruff / mypy / pytest green
- [ ] Frontend typecheck / lint / test / build green
- [ ] GitHub Actions CI green on Ubuntu+Windows matrices
- [ ] Sample reports and docs images present
- [ ] README 41 sections complete
