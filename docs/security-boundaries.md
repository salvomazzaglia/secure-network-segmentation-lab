# Security boundaries

## Hard boundaries in v1.0

| Boundary | Enforcement |
|----------|-------------|
| No live discovery | Code and CI forbid scanners / interface inspection |
| No mutation | No CoA, SNMP SET, VLAN writes, firewall commits |
| Local bind | Default `127.0.0.1` |
| Synthetic fixtures | Privacy guards on tracked files |
| Declarative policy | No executable policy expressions |

## Trust zones inside the lab

Management and Infrastructure are privileged teaching tiers. Guest/IoT/Quarantine demonstrate restriction. Boundaries are simulated reachability, not enforced ACLs.
