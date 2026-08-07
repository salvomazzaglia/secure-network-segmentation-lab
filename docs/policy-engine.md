# Policy engine

Operates on normalized device profiles. Declarative YAML only — no eval, embedded Python, Jinja execution, or shell.

## Inputs

device_class, confidence bounds, connection type, ownership label, approval/security state, source/destination segment, tags.

## Decisions

`keep`, `recommend_move`, `quarantine`, `require_approval`, `deny_transition`, `no_match`.

## Result fields

`policy_id`, `matched_rule`, `current_segment`, `recommended_segment`, `decision`, `approval_required`, `reason`, `confidence`, `policy_version`, `generated_at_utc`, plus change label **PROPOSED / SIMULATED — NOT APPLIED**.

## Rule IDs

Segmentation: `SNSL-SEG-xxx` in `config/segmentation-policy.yml`.

Implicit default permit is **false**. Unknown/uncertain paths prefer quarantine with approval.
