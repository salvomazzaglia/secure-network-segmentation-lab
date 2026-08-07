# Adapter model

Registered adapters (`radius`, `dhcp`, `arp`, `lldp`, `fdb`, `snmp`, `wlan`, `firewall`) exist as **read-only plan** stubs.

| Field | v1.0 value |
|-------|------------|
| mode | live-adapter-plan |
| capability | read-only-plan |
| connects | false |
| mutates | false |

CLI `adapter-plan` emits DRY-RUN steps and warnings. No sockets to infrastructure devices are opened.
