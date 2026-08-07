## Summary

<!-- What does this PR change and why? -->

## Synthetic / privacy checklist

- [ ] No RFC1918 addresses in tracked fixtures
- [ ] MACs are locally administered (`02:`) in examples/synthetic data
- [ ] No real vendor names, SSIDs, hostnames, or credentials
- [ ] No `shell=True`, `eval(`, unsafe YAML, `pull_request_target`, or self-hosted runners
- [ ] No network discovery / enforcement behavior introduced for v1.x

## Test plan

- [ ] `python scripts/validate-repository.py`
- [ ] Backend: ruff / mypy / pytest (as applicable)
- [ ] Frontend: typecheck / lint / test / build (if UI touched)
- [ ] Docs updated when behavior or safety boundaries change

## Notes

<!-- Optional: screenshots must show SYNTHETIC DEMONSTRATION DATA -->
