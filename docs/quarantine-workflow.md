# Quarantine workflow

Unknown and low-confidence devices default to Quarantine in synthetic simulation.

## Conceptual reachability

**Allow:** DHCP, DNS, NTP, limited Internet egress, optional onboarding.  
**Deny:** Management, Infrastructure, Trusted, IoT east-west, other Quarantine clients.

This is a logical policy model only. No firewall rule is applied.

## UI requirements

Visually emphasize quarantine restrictions and display simulated banners. Quarantine recommendations create approval-gated audit events without mutating networks.
