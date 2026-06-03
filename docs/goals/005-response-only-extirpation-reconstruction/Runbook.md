# Runbook

## Working Directory

```bash
cd /Users/bwbrook/papers/spatext
```

## Operating Rules

- Read `Goal.md`, `Plan.md`, `Runbook.md`, and `Log.md` before changing files.
- Follow repo-local `AGENTS.md`.
- Keep reconstruction response-only.
- Use hidden truth only in evaluation-only diagnostics.
- Do not start ABC, POM, fitting, parameter inference, real-data analysis, or
  remote compute.
- Do not commit or push in this goal.

## Initial Checks

```bash
git status --short --branch
git log --oneline --decorate --max-count=6
git ls-files -m -o --exclude-standard
```

Expected starting state:

- branch is `main...origin/main`,
- Goal 004 publication commits are present,
- the only new untracked paths should be this Goal 005 packet unless the
  supervisor has added more instructions.

If unexpected tracked edits are present outside this goal, stop and report.

## Prerequisite Observation Bundle

Rebuild the current deterministic truth and response-observation artifacts
before reconstruction:

```bash
uv sync --all-groups
uv run python scripts/build_synth_small_predator_truth.py
uv run python scripts/inspect_synth_small_predator_truth.py
uv run python scripts/build_synth_small_observations.py
uv run python scripts/inspect_synth_small_observations.py
jq '{passed}' artifacts/synth_small_observations/inspection/verification.json
jq '{passed, finite_metrics: ([.metrics[] | type == "number"] | all)}' artifacts/synth_small_observations/inspection/recoverability_smoke.json
```

## Implementation Targets

Likely files to add or update:

```text
spec/synth_small_extirpation_reconstruction.md
scripts/reconstruct_synth_small_extirpation.py
scripts/inspect_synth_small_extirpation_reconstruction.py
src/spatext/synth/small/__init__.py
src/spatext/synth/small/reconstruction.py
tests/test_synth_small_extirpation_reconstruction.py
spec/report_log.md
docs/goals/005-response-only-extirpation-reconstruction/Log.md
```

Do not edit Goal 001-004 files unless a directly relevant documentation link
must be corrected.

## Reconstruction Commands

After implementation, run:

```bash
uv run python scripts/reconstruct_synth_small_extirpation.py
uv run python scripts/inspect_synth_small_extirpation_reconstruction.py
```

Expected artifact directory:

```text
artifacts/synth_small_extirpation_reconstruction/
```

Expected files:

```bash
test -s artifacts/synth_small_extirpation_reconstruction/reconstruction_config.json
test -s artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv
test -s artifacts/synth_small_extirpation_reconstruction/time_detection_summary.csv
test -s artifacts/synth_small_extirpation_reconstruction/verification.json
test -s artifacts/synth_small_extirpation_reconstruction/evaluation_metrics.json
test -s artifacts/synth_small_extirpation_reconstruction/report.md
```

## Response-Only Boundary Checks

Run:

```bash
python - <<'PY'
from csv import DictReader
from pathlib import Path

path = Path("artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv")
with path.open(newline="", encoding="utf-8") as handle:
    rows = list(DictReader(handle))
assert rows, "site_reconstruction.csv must contain rows"
forbidden = {
    "driver_arrival",
    "predator_pressure",
    "true_extirpation",
    "extirpation_lag",
    "extirpated_by_end",
    "initial_abundance",
    "final_abundance",
}
columns = set(rows[0])
overlap = columns & forbidden
assert not overlap, f"response-only reconstruction leaked hidden truth columns: {sorted(overlap)}"
print({"row_count": len(rows), "column_count": len(columns)})
PY
```

Then:

```bash
jq '{passed}' artifacts/synth_small_extirpation_reconstruction/verification.json
jq '{passed, metrics}' artifacts/synth_small_extirpation_reconstruction/evaluation_metrics.json
```

## Focused Tests

Run:

```bash
uv run pytest tests/test_synth_small_extirpation_reconstruction.py --no-cov
```

## Full Quality Lane

Run:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

## Final Git Review

Do not stage, commit, or push.

Report:

```bash
git status --short --branch
git diff --stat
git diff -- docs/goals/005-response-only-extirpation-reconstruction/Log.md spec/report_log.md | sed -n '1,220p'
```

The final response should include:

- implementation summary,
- key reconstruction metrics,
- hidden-truth evaluation metrics,
- validation commands and results,
- final git status,
- residual scientific risks,
- recommended next step.
