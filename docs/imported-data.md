# Imported data

Imports accept sanitized bundles conforming to `schemas/import.schema.json`.

## Requirements

- Documentation IPs / `2001:db8::/32`
- LAA MACs (`02:`)
- Fictional vendors and hostnames
- `privacy_reviewed: true` only after manual review
- Banner fields present

Reject bundles that contain RFC1918, real OUIs, secrets, or unsanitized topology exports.

See `examples/sanitized-import/`.
