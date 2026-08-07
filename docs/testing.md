# Testing

## Backend

Target: large meaningful pytest suite covering config validation, classification, confidence bands, policy decisions, reachability, quarantine, approvals, topology provenance, privacy masking, import rejection, simulator determinism, API handlers, and report banners.

Commands:

```bash
cd backend
python -m pip install -e ".[dev]"
python -m ruff check src tests ../scripts
python -m ruff format --check src tests ../scripts
python -m mypy src
python -m pytest -q
```

## Frontend

Vitest + React Testing Library for state, API client mocks, and view-mode rendering. ESLint, Prettier, TypeScript strict, Vite production build.

## Repository guards

```bash
python scripts/validate-repository.py
python scripts/run-full-ci.py
```

Guards fail on RFC1918 in fixtures, dangerous CI triggers, `shell=True`, `eval(`, and scanner references in executable contexts.
