# Threat model

## Assets

- Topology
- Inventory
- Policy
- Classification evidence
- Imported metadata
- Approvals
- Audit log
- Network identifiers
- Reports
- UI data

## Threats and mitigations

| Threat | Mitigation | Residual risk |
|--------|------------|---------------|
| Leaking real topology | Synthetic-only tracked data; import review | Operator bypasses review |
| Leaking MAC/IP/SSID | Documentation ranges; LAA MACs; masking modes | Full mode misuse |
| Exposing RADIUS secrets | Secrets forbidden; adapters dry-run | Future adapter mistakes |
| Unsafe imported data | Schema + privacy validation | Novel obfuscation |
| Malicious YAML | Declarative parse; SafeLoader; no exec | Parser bugs |
| JSON resource exhaustion | Size limits in API/import paths | Huge local files |
| Path traversal / symlink escape | Root confinement for file ops | OS-level races |
| HTML injection | Escape dynamic report/UI values | Missed sink |
| WebSocket abuse | Local bind; no authz beyond localhost trust | Shared-host exposure |
| Unauthorized API binding | Default 127.0.0.1; document risk of override | Misconfiguration |
| Policy manipulation | Versioned audited policy files | Local file write access |
| Approval bypass | Explicit workflow records | Direct DB edits |
| Classification poisoning | Provenance + weights transparency | Bad imports |
| Confidence overstatement | Document heuristic nature | UI wording drift |
| Unsafe future enforcement | Roadmap gates; v1.0 has no enforcement | Premature feature |
| False physical-location claims | Explicit 3D disclaimer | User assumption |
| Reachability false confidence | "Intended policy only" labels | Operator trust |
| Stale inventory | Staleness + drift severities | Ignored alerts |
| Malformed LLDP/FDB import | Reject invalid sanitized input | Parser gaps |
| Supply-chain compromise | Pin Actions SHAs; Dependabot | Upstream malice |
| GitHub Action compromise | SHA pins; least permissions (`contents: read`) | Re-tag attacks mitigated, not eliminated |

## Out of scope

Production NAC efficacy, live adversary simulation against real networks, and formal anonymity certification.
