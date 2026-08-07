# API

Base URL (default): `http://127.0.0.1:8765`

All payloads are synthetic lab state. Version 1.0 never applies network changes.

## REST

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Liveness |
| GET | `/api/v1/lab` | Lab snapshot summary |
| GET | `/api/v1/devices` | Inventory list |
| GET | `/api/v1/devices/{id}` | Device detail |
| GET | `/api/v1/segments` | Segment catalog |
| GET | `/api/v1/topology` | Nodes and edges |
| GET | `/api/v1/classifications` | Classification results |
| GET | `/api/v1/policy/decisions` | Segmentation decisions |
| GET | `/api/v1/reachability` | Reachability matrix/results |
| GET | `/api/v1/drift` | Drift findings |
| GET | `/api/v1/events` | Recent events |
| GET | `/api/v1/audit` | Audit records |
| GET | `/api/v1/adapters` | Adapter registry / plans |
| POST | `/api/v1/simulation/reset` | Reset synthetic sim |
| POST | `/api/v1/simulation/step` | Single sim step |
| POST | `/api/v1/simulation/run` | Run scenario |
| POST | `/api/v1/approvals` | Record simulated approval |

## WebSocket

Event stream for simulator/audit updates. No external broker. Clients should treat events as synthetic.

## Safety

Do not bind `0.0.0.0` for demos. Prefer loopback. Responses include synthetic banners where applicable.
