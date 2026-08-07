# Device classification

## Classes

firewall, router, switch, access_point, server, workstation, laptop, smartphone, tablet, printer, camera, nas, media_device, iot, network_appliance, unknown.

## Output shape

```json
{
  "device_id": "SYNTHETIC-PRN-01",
  "predicted_class": "printer",
  "confidence": 0.91,
  "alternatives": [{"class": "iot", "confidence": 0.42}],
  "evidence": [],
  "classification_status": "classified"
}
```

## Statuses

| Status | Meaning |
|--------|---------|
| `classified` | Confidence above classified threshold |
| `uncertain` | Mid-band confidence |
| `unknown` | Insufficient evidence |
| `manually_reviewed` | Operator override recorded |

## Engine constraints

- Deterministic, explainable scoring
- **No machine-learning model** in v1.0
- Evidence weights from `config/evidence-weights.json`
- UI must answer "Why classified?" with weighted evidence

Classification never assigns VLANs. Policy consumes the profile afterward.
