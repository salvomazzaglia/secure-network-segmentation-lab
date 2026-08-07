# Confidence model

`confidence` is a **normalized heuristic evidence score**, not a statistical probability and not a calibrated likelihood.

## Default weights

| Evidence | Weight |
|----------|--------|
| vendor_hint | 0.15 |
| dhcp_fingerprint | 0.20 |
| hostname_pattern | 0.10 |
| services | 0.25 |
| reported_os | 0.15 |
| historical_consistency | 0.15 |

## Default thresholds

| Band | Score | Status |
|------|-------|--------|
| High | ≥ 0.80 | classified |
| Mid | 0.60–0.79 | uncertain |
| Low | < 0.60 | unknown |

Thresholds are configurable in `config/default.config.json` / `demo.config.json`.

## Honesty requirements

- Do not overstate certainty in UI copy
- Show alternatives when present
- Treat low confidence as quarantine-leaning policy input, not proof of malice
