# Runbook

From `/Users/bwbrook/papers/spatext`:

```bash
git status --short --branch --untracked-files=all
git diff --check
uv run pytest tests/test_synth_medium_response_reconstruction_benchmark.py --no-cov
uv run pytest tests/test_synth_medium_observation_design.py --no-cov
uv run pytest tests/test_synth_medium_spread_impact.py --no-cov
uv run pytest tests/test_synth_medium_landscape.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run python scripts/benchmark_synth_medium_response_reconstruction.py
git status --ignored --short artifacts dist
```

Generated artifacts should remain ignored/unstaged under:

```text
artifacts/synth_medium_response_reconstruction_benchmark/
```

Do not commit or push during implementation review.
