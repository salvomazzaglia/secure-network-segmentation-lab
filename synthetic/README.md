# Synthetic lab data

All files in this directory are **fictional demonstration data**.

- IP addresses use only documentation ranges: `192.0.2.0/24`, `198.51.100.0/24`,
  `203.0.113.0/24`, and `2001:db8::/32`.
- MAC addresses are locally administered addresses starting with `02:`.
- Hostnames, SSIDs (`SYNTHETIC-LAB` / `SYNTHETIC-GUEST` / `SYNTHETIC-IOT`), and
  vendors (for example “Synthetic Devices Ltd.”) are fictional.
- VLAN IDs (210–260) are **SYNTHETIC VLAN ID — EXAMPLE ONLY**.
- No data was collected from a real network. RFC1918 private addresses are not used.

Regenerate with:

```bash
python scripts/generate-synthetic-lab.py --seed 42
```

Or via the CLI after installing the backend package:

```bash
snsl generate-demo --seed 42
```

Every simulated change is labelled **PROPOSED / SIMULATED — NOT APPLIED**.
