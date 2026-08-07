# Approval workflow

## Actions

`approve`, `reject`, `keep_quarantined`, `choose_alternate_segment`.

## Record fields

`approval_id`, `device_id`, previous/recommended/chosen segments, `decision`, `operator_label`, `justification`, timestamps, `policy_id`, `synthetic`.

Use `operator_label: SYNTHETIC-OPERATOR` in fixtures — never the developer's personal name.

## Safety

> SIMULATED APPROVAL — NO NETWORK CHANGE APPLIED

Approval updates simulated lab state only. No RADIUS CoA, no switch VLAN writes, no firewall commits.
