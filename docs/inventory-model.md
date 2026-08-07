# Inventory model

The inventory is the normalized device store consumed by classification, policy, topology, and UI.

## Device record

Key fields: `device_id`, `alias`, `mac`, optional `ipv4`/`ipv6`, `hostname`, fictional `vendor`, `device_class_hint`, `connection_type`, `current_segment`, `recommended_segment`, `security_state`, online/stale flags, timestamps, tags, wireless/wired attachment metadata, `ownership_label`, `provenance`, `source_mode`.

See `schemas/device.schema.json` and `examples/sample-inventory.json`.

## Security states

`approved`, `restricted`, `quarantined`, `uncertain`, `policy_violation`, `offline`, `awaiting_approval`.

## Staleness

Configurable `stale_after_seconds` marks devices not seen recently. Stale inventory is drift signal, not automatic breach.

## Privacy

Masked mode never exposes raw non-sanitized imported values. Documentation ranges and LAA MACs only in tracked samples.
