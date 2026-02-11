# AGENTS.md

## How to run tests
- Install: `python -m pip install -e .[dev]`
- Run full tests: `pytest`
- Lint/format checks: `ruff check src tests && black --check src tests`
- Run quick benchmark: `router bench --suite quick`

## Code style rules
- Python 3.11+ with type hints on public functions.
- Keep modules small and explicit; avoid hidden magic.
- Use `black` formatting and `ruff` lint rules.
- Prefer deterministic behavior in tests; default to `MockAdapter`.

## P0 vs P1 issue definitions
- **P0**: incorrect routing decision under configured budgets, crash in CLI, broken tests/CI, trace write failures.
- **P1**: documentation inaccuracies, minor metric/report formatting issues, non-critical ergonomics.

## How to add new adapters
1. Add adapter class in `src/ai_decision_router/adapters.py` implementing `BaseAdapter.generate`.
2. Add provider selection in `DecisionRouter._adapter`.
3. Document required env vars in README.
4. Add tests covering deterministic behavior or mocking external calls.

## How to add new policies
1. Implement a `BasePolicy` subclass in `src/ai_decision_router/policies.py`.
2. Add policy selection in `DecisionRouter._policy`.
3. Add config fields in `PolicyConfig` if needed.
4. Add unit tests for routing behavior and budget handling.
