# Reachability analysis

Logical engine inputs: source segment, destination segment, service category, declarative rules from `config/reachability-policy.yml`.

## Decisions

`allowed`, `denied`, `conditional`, `unknown`.

## Examples

- Guest → Management = denied
- IoT → Management = denied
- Trusted → Internet secure_web = allowed
- Quarantine → Management = denied
- Quarantine → DNS = allowed

Path explanations cite rule IDs (`SNSL-RCH-xxx`). The engine models **intended policy only** — no real firewall verification.
