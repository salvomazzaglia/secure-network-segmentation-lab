# Privacy and anonymization

## Non-negotiables

- No real environment data in this repository
- No host discovery against live networks
- No secrets (RADIUS, SNMP communities, API tokens, private keys)
- Screenshots must display **SYNTHETIC DEMONSTRATION DATA** or be refused

## Why documentation IP ranges?

RFC 5737 / RFC 3849 documentation addresses are reserved for examples. Using them prevents accidental collision with production addressing and makes fixture intent obvious during review.

## Why locally administered MACs (`02:`)?

The universal/local bit marks addresses as locally administered. Lab fixtures use `02:` prefixes so examples cannot be mistaken for burned-in vendor OUIs from real hardware.

## Why fictional vendors?

Real vendor strings in fixtures create false attribution and can leak organizational purchasing context. The lab uses names such as "Synthetic Devices Ltd." and "Demo IoT Corporation".

## Why synthetic VLAN IDs?

VLAN 210–260 in this project are demonstration labels only. They must not be copied from any external or local production configuration.

## Why real topology is never committed

Topology discloses trust boundaries, wireless placement heuristics, and asset roles. Only synthetic topologies generated from seed parameters are tracked.

## Sanitized import workflow

1. Operator exports data outside this repo
2. Operator masks/hashes identifiers
3. Operator maps addresses into documentation ranges and `02:` MACs
4. Bundle sets `privacy_reviewed: true` only after human review
5. Lab imports the bundle in `imported` mode

> Do not publish sanitized data until it has been manually reviewed. Automated masking reduces disclosure risk but is not a guarantee of anonymization.

## Reporting modes

| Mode | Behavior |
|------|----------|
| `masked` | Default; redact sensitive fields in exports |
| `hashed` | Stable irreversible aliases |
| `full` | Local operator use only; never commit |

## Pseudonymization vs anonymization

Pseudonymization replaces identifiers but may remain joinable. Anonymization aims to prevent re-identification. This lab performs **masking and synthetic substitution**, not a formal anonymity proof.

## Screenshot restrictions

Capture only from `127.0.0.1` with a temporary browser profile. Refuse capture if the synthetic banner is absent.

## Git history checks

Before publication, scan staged and historical content for RFC1918, real OUIs, credentials, and network exports. Use `python scripts/validate-repository.py`.

## Publication checklist

- [ ] Privacy guard passes
- [ ] Examples use documentation IPs and `02:` MACs only
- [ ] No real screenshots or PCAPs
- [ ] `SECURITY.md` and threat model reviewed
- [ ] Sanitized imports manually reviewed
