# Examples

All fixtures in this directory are **synthetic demonstration data**.

> Every device, address, MAC, VLAN, SSID, topology relationship, signal value,
> service observation, policy decision, and event published in this repository
> is synthetic. No real network or homelab data is included.

## Contents

| File | Purpose |
|------|---------|
| `sample-inventory.json` | Inventory report envelope with synthetic devices |
| `sample-classification-report.json` | Classification outcomes with evidence |
| `sample-policy-report.json` | Segmentation policy decisions |
| `sample-reachability-report.json` | Logical reachability matrix samples |
| `sample-topology.json` | Illustrative topology nodes/edges |
| `sample-audit-log.jsonl` | Synthetic audit records |
| `sanitized-import/sample-sanitized-inventory.json` | Example sanitized import bundle |

## Address policy

- IPv4: documentation ranges only (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`)
- IPv6: `2001:db8::/32` only
- MAC: locally administered addresses starting with `02:`
- Vendors: fictional names from `config/synthetic-vendors.json`
- SSIDs: `SYNTHETIC-LAB`, `SYNTHETIC-GUEST`, `SYNTHETIC-IOT`

## Sanitized import

Do not publish sanitized data until it has been manually reviewed. Automated
masking reduces disclosure risk but is not a guarantee of anonymization.

## Regenerating

After installing the package:

```bash
python scripts/generate-sample-reports.py
```
