# Contributing

Thank you for contributing to **secure-network-segmentation-lab**.

## Rules

1. Keep all public fixtures **synthetic**.
2. Use documentation IP ranges only (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`, `2001:db8::/32`).
3. Use locally administered MACs beginning with `02:`.
4. Do not add real SSIDs, hostnames, vendors, VLAN IDs from private labs, or RFC1918 examples.
5. Do not implement enforcement, SNMP SET, RADIUS CoA, Disconnect-Request, or configuration mutation in v1.0.
6. Classification and segmentation decisions must remain separate.
7. Prefer explainable deterministic logic over opaque models.

## Development

```bash
cd backend
python -m pip install -e ".[dev]"
python ../scripts/generate-synthetic-lab.py
python -m pytest
```

```bash
cd frontend
npm ci
npm test
npm run build
```

## Pull requests

Use the repository PR template. CI must stay on GitHub-hosted runners with actions pinned to full commit SHAs.
