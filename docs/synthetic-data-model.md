# Synthetic data model

All published lab content is fictional demonstration data.

## Identity conventions

- Device IDs: `SYNTHETIC-*`
- Hostnames: `SYNTHETIC-*`
- SSIDs: `SYNTHETIC-LAB`, `SYNTHETIC-GUEST`, `SYNTHETIC-IOT`
- Operators in audits: `SYNTHETIC-OPERATOR`
- Vendors: fictional entries from `config/synthetic-vendors.json`

## Addressing

| Kind | Allowed |
|------|---------|
| IPv4 | `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` |
| IPv6 | `2001:db8::/32` |
| MAC | Locally administered, prefix `02:` |
| VLAN | Demo IDs 210–260 labeled **SYNTHETIC VLAN ID — EXAMPLE ONLY** |

RFC1918 private ranges must not appear in tracked fixtures.

## Segments

Logical prefixes such as `SEGMENT-NET-210` represent security zones. Only selected demo views map to documentation IPv4 ranges; not every VLAN pretends to own a unique global subnet.

## Provenance

Every fact carries one of: `observed`, `reported`, `inferred`, `synthetic`, `operator_defined`. Categories are never silently merged.

## Lab scale (target)

Approximately 35–40 nodes including infrastructure, wired and wireless endpoints, intentional quarantine/uncertain/drift cases, and offline/stale records.
