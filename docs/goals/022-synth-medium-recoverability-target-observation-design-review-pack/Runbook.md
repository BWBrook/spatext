# Runbook

From `/Users/bwbrook/papers/spatext`:

```bash
git status --short --branch --untracked-files=all
git diff --check
uv run pytest tests/test_synth_medium_recoverability_target_observation_design.py --no-cov
uv run pytest tests/test_synth_medium_observation_design_counterfactual_screen.py --no-cov
uv run pytest tests/test_synth_medium_response_reconstruction_benchmark.py --no-cov
uv run pytest tests/test_synth_medium_observation_design.py --no-cov
uv run pytest tests/test_synth_medium_spread_impact.py --no-cov
uv run pytest tests/test_synth_medium_landscape.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run python scripts/build_synth_medium_recoverability_target_observation_design.py
git status --ignored --short artifacts dist
```

Expected CLI output includes:

- baseline `structured_response_observed_default`
- baseline primary rule `final_absence_run_1`
- candidate regime count `8`
- best field-plausible regime
  `integrated_recoverability_target_panel`
- generated bundle under
  `artifacts/synth_medium_recoverability_target_observation_design/`

Do not stage generated artifacts or build outputs.
