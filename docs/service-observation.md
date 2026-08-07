# Service observation

Services carry provenance (`observed`, `reported`, `inferred`, plus lab `synthetic` / `operator_defined` where applicable).

## Categories

web, secure_web, ssh, dns, ntp, dhcp, printing, file_service, media, database, management, unknown.

## Constraints

- No active port scanning
- No host probing
- Port maps to a **category hint** only — never product/version inference unless explicitly supplied in synthetic/imported metadata

Example: TCP/443 → `secure_web` (observed), not "Apache version X".
