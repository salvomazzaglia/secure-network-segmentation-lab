# RADIUS and dynamic VLAN model

v1.0 models the **concept** without connecting to a RADIUS server.

## Synthetic attributes

Authentication result, identity alias, calling-station synthetic MAC, NAS synthetic identifier, SSID, assigned segment, VLAN recommendation.

Representational tunnel attributes (conceptual): Tunnel-Type, Tunnel-Medium-Type, Tunnel-Private-Group-ID.

## Explicitly out of scope for v1.0

- Shared secrets
- Packet transmission
- RADIUS CoA
- Disconnect-Request

## Future architecture (not implemented)

Classifier → policy engine → authorization decision → RADIUS adapter → dynamic VLAN

Adapter output today: **DRY-RUN PLAN** only (`config/adapter-registry.json`).
