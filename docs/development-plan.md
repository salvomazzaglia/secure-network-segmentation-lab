# Development Plan — secure-network-segmentation-lab 1.0.0

## Objective
Vendor-neutral, offline-first Secure Network Segmentation Lab demonstrating
classification → policy → segment recommendation with approval gates, quarantine,
reachability, and interactive 3D security visualization — all synthetic.

## Critical separation
Evidence → Classification → Confidence → Device profile → Policy → Recommended segment
Never: Evidence → VLAN directly.

## Privacy
Zero real network data. Documentation IPs only. LAA MACs (02:). Fictional vendors.
No host discovery. No enforcement in v1.0.

## Phases
1. Structure & configs
2. Backend models / SQLite / privacy
3. Synthetic lab generator
4. Classification + confidence
5. Policy + approval + reachability
6. Topology / wireless / services / drift
7. Simulator / adapters / imports
8. API / WebSocket / CLI
9. Frontend dashboard + 3D
10. Reports / tests / CI / docs
11. Screenshots / privacy audit / git init

## Acceptance
See README and final-release-checklist.md.
