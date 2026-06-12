# Plan

## 1. Confirm State And Branch

- Report actual working directory and Git state.
- Fetch `origin`.
- Confirm `origin/main` is at `91b5df7` or newer.
- Create local branch
  `codex/spatext-goal013-observation-support-counterfactual-screen` from
  `origin/main`.
- If branch creation or checkout fails, stop and report the exact blocker. Do
  not force, delete, reset, rebase, or repair by improvisation.

## 2. Refresh Contracts

- Read `AGENTS.md`, `README.md`, `spec/problem_statement.md`,
  `spec/theory.md`, and `spec/report_log.md`.
- Read these specs:
  - `spec/synth_small_observations.md`;
  - `spec/synth_small_extirpation_reconstruction.md`;
  - `spec/synth_small_response_screen_evaluation.md`;
  - `spec/synth_small_summary_vector.md`;
  - `spec/synth_small_compatibility_screen.md`;
  - `spec/synth_small_false_negative_mechanism_audit.md`.
- Read Goal 009 through Goal 012 packets and this Goal 013 packet.
- Read current source/test surfaces for observations, reconstruction,
  response-screen evaluation, summary vectors, compatibility screening, and
  false-negative auditing.

## 3. Write The Spec First

- Add `spec/synth_small_observation_support_counterfactual_screen.md`.
- Define:
  - purpose and scope;
  - disk input contract;
  - scenario IDs and scenario semantics;
  - per-site resolution schema;
  - scenario reconstruction summaries;
  - scenario summary-vector/compatibility outputs;
  - recommendation classes;
  - output artifact contract;
  - synthetic-only, evaluation-only, counterfactual-only, and non-inference
    boundary rules;
  - acceptance criteria.

## 4. Test First

- Add `tests/test_synth_small_observation_support_counterfactual_screen.py`.
- Cover:
  - disk-first loading of prerequisite artifacts;
  - status-quo reconciliation with Goal 010-012 counts;
  - one per-scenario resolution row for every Goal 012 false-negative site;
  - scenario definitions emitted with stable IDs;
  - finite-target count and false-negative count reconciliation;
  - scenario compatibility score/ranking outputs;
  - recommendation classification;
  - output artifact writing;
  - CLI execution;
  - synthetic-only/evaluation-only/counterfactual-only labels.
- Run the focused test and confirm it fails before implementation.

## 5. Implement The Counterfactual Screen

- Add `src/spatext/synth/small/observation_support_counterfactual_screen.py`.
- Load required artifacts from disk.
- Build a small documented scenario set.
- Produce per-site counterfactual resolution rows for all Goal 012
  false-negative sites.
- Build scenario-level reconstructed target summaries without mutating the
  default reconstruction artifacts.
- Reuse existing summary-vector and compatibility-screen contracts where
  practical.
- Emit scenario summaries, scores, rankings, recommendation, verification, and
  a compact report.
- Do not mutate observations, reconstruction, response-screen evaluation,
  summary-vector, compatibility-screen, mismatch-audit, or Goal 012 artifacts.

## 6. Add CLI And Exports

- Add `scripts/run_synth_small_observation_support_counterfactual.py`.
- Export the public API from `src/spatext/synth/small/__init__.py`.

## 7. Update Docs And Log

- Update `README.md` with the counterfactual-screen surface and command.
- Update `AGENTS.md` if the authoritative spec list needs the new spec.
- Update `spec/report_log.md`.
- Update this goal `Log.md` throughout the run with checkpoints and validation
  evidence.

## 8. Validate

Run a proportionate validation ladder:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_observation_support_counterfactual_screen.py --no-cov
uv run pytest tests/test_synth_small_false_negative_mechanism_audit.py --no-cov
uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov
uv run pytest tests/test_synth_small_summary_vector.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the counterfactual CLI against local ignored artifacts:

```bash
uv run python scripts/run_synth_small_observation_support_counterfactual.py
```

## 9. Report And Wake Up

- Report changed files.
- Report validation results.
- Report scenario IDs and scenario semantics.
- Report status-quo reconciliation.
- Report which scenario, if any, restores finite-target count and
  compatibility.
- Report remaining blocker classes.
- Report recommendation class.
- Confirm generated artifacts remain unstaged.
- Confirm no commit or push was performed.
- Send a short wake-up to the SpatExt orchestrator thread when complete or
  blocked, then wait for review.
