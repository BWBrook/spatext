# Log

## 2026-06-23 - Orchestrator Delegation

Barry approved Goal 021 after accepting and publishing the Goal 020
response-reconstruction benchmark. The approved next step is a deterministic,
synthetic-only observation-design recoverability counterfactual screen over
the fixed Goal 017 landscape, Goal 018 spread-impact truth, Goal 019 published
observation design, and Goal 020 reconstruction benchmark.

The goal asks whether plausible field-like additional response-observation
support can make reconstruction credible enough for later fitting work, or
whether only an unrealistic diagnostic ceiling recovers signal. It explicitly
forbids changing prior goal contracts, adopting production observation or
reconstruction rules, fitting, inference, real-data analysis, broad sweeps,
remote compute, commits, pushes, generated-artifact staging, and Goal 022.

## 2026-06-23 - Action Implementation

Created branch
`codex/spatext-goal021-synth-medium-observation-design-counterfactual-screen`
from `origin/main` at the published Goal 020 commit
`8b85175164f245e677ff38bba3392625087443ea`.

Read repo-local instructions, README, Goal 017-020 specs/logs, and current
synth-medium landscape, spread-impact, observation-design, and
response-reconstruction modules before implementation.

Added focused tests first in
`tests/test_synth_medium_observation_design_counterfactual_screen.py`. The RED
check:

```bash
uv run pytest tests/test_synth_medium_observation_design_counterfactual_screen.py --no-cov
```

initially failed because the new Goal 021 API did not yet exist.

Implemented the Goal 021 review-pack footprint:

- `spec/synth_medium_observation_design_counterfactual_screen.md`
- `src/spatext/synth/medium/observation_design_counterfactual_screen.py`
- `scripts/screen_synth_medium_observation_design_counterfactuals.py`
- `tests/test_synth_medium_observation_design_counterfactual_screen.py`
- exports in `src/spatext/synth/medium/__init__.py`
- README, AGENTS, and report-log updates

Focused tests passed after implementation:

```bash
uv run pytest tests/test_synth_medium_observation_design_counterfactual_screen.py --no-cov
```

with `5` tests passing.

Generated review bundle:

```text
artifacts/synth_medium_observation_design_counterfactual_screen/
```

CLI smoke:

```bash
uv run python scripts/screen_synth_medium_observation_design_counterfactuals.py
```

Output:

- baseline regime `structured_response_observed_default`
- baseline primary rule `final_absence_run_1`
- regime count `6`
- rule count `3`
- best plausible regime `final_absence_confirmation_support`
- best plausible rule `final_absence_run_1`
- best plausible finite recall `0.582186989974`
- best plausible false negatives `1792`
- ceiling finite recall `1.0`
- ceiling false negatives `0`
- decision recommendation `only_unrealistic_observation_ceiling_recovers_signal`
- `15` files written

Headline regenerated outcomes:

- Baseline `structured_response_observed_default` / `final_absence_run_1`:
  finite recall `0.524364653765`, `2040` false negatives, `304` false
  positives, median absolute error `16.1861668722`, p90 absolute error
  `56.5705868251`, `809` large errors, loss `1.89367625628`.
- Best plausible by recoverability:
  `final_absence_confirmation_support` / `final_absence_run_1`, finite recall
  `0.582186989974`, `1792` false negatives, `403` false positives, median
  absolute error `15.0058585723`, p90 absolute error `56.588358166`, `864`
  large errors, loss `1.86936751222`.
- Diagnostic ceiling:
  `near_perfect_response_observation_ceiling` /
  `midpoint_after_last_detection`, finite recall `1.0`, `0` false negatives,
  `0` false positives, median absolute error `2.92925809436`, p90 absolute
  error `5.37040065744`, `0` large errors, loss `0.066451285388`.

Interpretation: plausible field-like observation support improves some pieces
of the published baseline but does not meet reconstruction-readiness gates.
Only the unrealistic diagnostic ceiling recovers the signal cleanly, so the
screen recommends against fitting from these response-only designs.

Final validation completed:

- `git status --short --branch --untracked-files=all`
- `git diff --check`
- `uv run pytest tests/test_synth_medium_observation_design_counterfactual_screen.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_response_reconstruction_benchmark.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_observation_design.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_spread_impact.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_landscape.py --no-cov`
  (`5` passed)
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest` (`118` passed, coverage `93.77%`)
- `uv build`
- `uv run python scripts/screen_synth_medium_observation_design_counterfactuals.py`
  (`15` files written)
- `git status --ignored --short artifacts dist` (`!! artifacts/`, `!! dist/`)

Final branch/status:

```text
## codex/spatext-goal021-synth-medium-observation-design-counterfactual-screen...origin/main
 M AGENTS.md
 M README.md
 M spec/report_log.md
 M src/spatext/synth/medium/__init__.py
?? docs/goals/021-synth-medium-observation-design-counterfactual-screen/Goal.md
?? docs/goals/021-synth-medium-observation-design-counterfactual-screen/Log.md
?? docs/goals/021-synth-medium-observation-design-counterfactual-screen/Plan.md
?? docs/goals/021-synth-medium-observation-design-counterfactual-screen/Runbook.md
?? scripts/screen_synth_medium_observation_design_counterfactuals.py
?? spec/synth_medium_observation_design_counterfactual_screen.md
?? src/spatext/synth/medium/observation_design_counterfactual_screen.py
?? tests/test_synth_medium_observation_design_counterfactual_screen.py
```

Generated artifacts and build outputs remained ignored and unstaged. No Goal
017 landscape change, Goal 018 truth change, Goal 019 observation-design
change, Goal 020 reconstruction-benchmark change, production observation
design adoption, production reconstruction-rule adoption, fitting, ABC, POM,
likelihood, MCMC, posterior, parameter recovery, real-data analysis, broad
sweep, remote compute, commit, push, generated-artifact staging, or Goal 022
work was performed.

## 2026-06-23 - Review Visual-Layout Polish

Review feedback accepted the scientific/numerical result but found a visual
decision-table layout issue: the display label `midpoint_after_last_detection`
in `recoverability_decision_montage.svg` overlapped the recall column.

Changes:

- Added a deterministic visual-regression test that estimates SVG text right
  edges and verifies decision-table cells do not intrude into adjacent columns.
  The test failed against the pre-polish SVG with the rule label extending
  past the safe rule-column boundary.
- Updated the decision-table renderer to use bounded display labels in each
  visual column.
- Added the explicit display label `midpoint_after_last_det` for the long
  `midpoint_after_last_detection` rule ID. The underlying CSV/ranking data
  still preserve the full rule ID.
- Updated the spec to record the bounded decision-table visual contract.
- Regenerated the ignored Goal 021 artifact bundle.

No counterfactual definitions, thresholds, reconstruction rules, ranking data,
recommendation class, numerical outcomes, production observation or
reconstruction rule, fitting, inference, real-data, remote-compute, commit,
push, generated-artifact staging, publication, or Goal 022 work was changed.
