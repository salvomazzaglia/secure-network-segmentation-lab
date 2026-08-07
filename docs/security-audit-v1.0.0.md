# Security / Privacy Audit — v1.0.0

## Audit methodology

1. Manual review of repository structure and source modes (synthetic / imported / live-adapter-plan).
2. Automated scan of `synthetic/` and `examples/` for RFC1918 addressing.
3. Source scan for `shell=True`, live `eval(`, unsafe `yaml.load`, network discovery tools, and CI anti-patterns (`self-hosted`, `pull_request_target`).
4. Verification that adapter modules emit DRY-RUN plans with `connects=false` and `mutates=false`.
5. Verification that approval mutations require `synthetic=true` and refuse non-synthetic source modes.
6. Confirmation that wireless and wired visualization code does not convert RSSI to meters or claim cable length.

## Synthetic-address policy

- IPv4 documentation ranges only: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`
- IPv6 documentation: `2001:db8::/32`
- MACs: locally administered `02:` prefix
- VLAN IDs 210–260 labelled **SYNTHETIC VLAN ID — EXAMPLE ONLY**
- Logical prefixes `SEGMENT-NET-2xx` used where unique production subnets are not pretended

## Anonymization checks

- Privacy modes: masked (default), hashed (`SNSL_HASH_SALT`, never stored), full (warns)
- Tracked samples remain fully synthetic regardless of privacy mode
- Screenshot policy requires `SYNTHETIC DEMONSTRATION DATA`

## Tracked-file checks

- No RFC1918 addresses in synthetic fixtures
- No real MAC OUIs in fixtures
- No RADIUS secrets / SNMP communities / private keys tracked
- No PCAP/EVTX/network exports tracked
- CI uses GitHub-hosted runners; actions pinned to full commit SHAs

## Findings

| Finding | Severity | Status |
| --- | --- | --- |
| None: enforcement paths | — | No apply/enforce/CoA/Disconnect commands in v1.0 |
| None: RFC1918 in synthetic | — | Guard passed |
| Placeholder screenshots | Informational | Solid-color synthetic PNGs present; regenerate with live dashboard when desired |
| FastAPI `on_event` deprecation | Low | Functional; lifespan migration deferred |

## Corrections applied during audit

- Approval API request model moved to module scope for correct JSON body parsing
- Repository guard script focused on actionable source/CI risks rather than documentation mentions of forbidden future features
- mypy/ruff issues resolved for CI green

## Remaining limitations

- v1.0 does not enforce network changes
- Classification confidence is heuristic, not statistical probability
- 3D placement is illustrative
- Imported mode trusts operator-supplied sanitization and still requires manual review before publication
- Automated masking reduces disclosure risk but is **not** a guarantee of anonymization

## Conclusion

Repository is suitable for local public-release preparation under synthetic-only constraints. No host network discovery or enforcement was executed during this audit.
