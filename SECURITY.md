# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | yes       |

## Vulnerability classes of interest

- Privacy leakage / real-network-data exposure
- Unsafe import (path traversal, symlink escape, oversized payloads)
- Policy bypass / approval bypass
- Unsafe adapter behavior or unintended network mutation
- WebSocket/API exposure beyond localhost
- HTML injection in reports
- Future enforcement risk if adapters are extended unsafely

## Reporting

Please use **GitHub Private Vulnerability Reporting** on this repository.

Do not include real network inventories, RADIUS secrets, SNMP communities, or credentials in reports.

## Scope notes for v1.0

Version 1.0 is synthetic/offline-first and must not enforce network changes. Reports involving “missing enforcement” are out of scope for 1.0; reports involving accidental enforcement paths are in scope.
