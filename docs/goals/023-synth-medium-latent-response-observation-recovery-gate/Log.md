# Goal 023 Log

## 2026-07-11 - Approval And Operating Model

Barry approved Goal 023 after a supervisor-style project debrief and an
explicit operating-model transition.

The persistent `mink` action-agent thread is retired. SpatExt remains the
persistent project orchestrator and now directly supervises specialist
subagents for execution, scientific review, provenance, validation, artifact
review, and final publication review. Subagent reports are evidence leads; the
orchestrator verifies claims against the live repository and generated bundle.

The approved scientific direction is an explicit observation/process model,
but the first bounded gate fixes the Goal 018 predator-arrival surface and
tests a minimal latent prey-response transition jointly with its observation
model. It deliberately does not jump to full predator-spread fitting.

## 2026-07-11 - Baseline

Isolated worktree:

```text
/Users/bwbrook/.codex/worktrees/spatext/goal023
```

Branch and base:

```text
codex/spatext-goal023-latent-response-observation-gate
53462d0365babf2c8070714a930f69b4071af276
```

The canonical action repo was clean on `main...origin/main` at the same commit.

Baseline setup and full validation:

```text
uv sync --all-groups
uv run pytest
124 passed
93.81% coverage
```

No Goal 023 source implementation or generated artifact existed at baseline.

## Packet Draft And Review

The orchestrator drafted the four-file packet after two specialist packet
writers stalled without touching the worktree. Two independent read-only
reviewers then returned `REVISE`.

Blocking findings included:

- ambiguity between Goal 018 deterministic response truth and the new Goal 023
  stochastic response truth;
- unspecified model equations, null, estimands, profiles, replicates, gates,
  and recommendation precedence;
- insufficient separation of process-only, observation-only, dense joint, and
  imperfect joint recovery;
- an incomplete analyst/truth firewall;
- artifact names without schemas or source hashes;
- prose-only holdout protection;
- overlapping writer ownership and unauditable TDD evidence;
- unsafe final-review ordering before exact staging; and
- scheduled-count success being overstated as presence-only transportability.

The orchestrator accepted these findings and revised the packet to freeze the
exact model and estimator, define new Goal 023 stochastic truth, add nested
gates and misspecification controls, define source/artifact schemas, lock
holdout hashes and seeds, separate one writer from read-only reviewers, require
staged-diff final review, and emit a mandatory scheduled-count-only
transportability class.

Barry's standing operating instruction grants conditional exact-footprint
commit and push authority once the goal is accepted, fully validated, and
independently reviewed. No additional publication permission is required
unless a material scientific assumption or strategic trade-off emerges.

The same reviewers re-reviewed the first correction and again returned
`REVISE`. Remaining blockers were an internally reusable holdout, coarse fixed
profile grids, boundary-invalid null calibration, underdefined stress
generators, truth-bearing scenario labels reaching the estimator, descriptive
rather than literal schemas, oracle truth conflicting with the joint firewall,
and non-executable footprint guards.

The second correction:

- moved all source, test, spec, artifact-writer, and documentation work before
  the single holdout execution;
- added immutable tracked source-digest and holdout receipts;
- prohibited holdout reruns and made any post-exposure analytical change a
  stop requiring Barry and a fresh seed namespace;
- replaced fixed profile grids with adaptive bracketing and cutoff root-finding;
- moved `beta_driver = 0` into the interior of signed support;
- added an equal-emission submodel, familywise binomial gates, and
  parameter-specific error/interval-width limits;
- fully specified continuous-abundance and spatial-frailty stresses and made
  silent misspecification block acceptance;
- removed scenario/split/replicate metadata from the joint estimator and
  separated non-deployable oracle APIs;
- defined canonical source serialization, literal artifact fields/types/keys,
  and receipt schemas; and
- added executable branch, base, unstaged, untracked, and staged-allowlist
  assertions before final review and commit.

A third re-review found remaining protocol contradictions: tracked analytical
state was not hash-enforced across holdout, Task 0 could drop a frozen
estimand, the plan still named fixed-grid profiles, the equal-emission and
permuted-arrival controls used invalid null logic, stress warnings were not
operational, enum/JSON domains remained partly open, and receipts had an
immutable-versus-invalidation contradiction.

The third correction added a canonical pre-holdout tracked-state digest and
receipt, made rank failure a stop, made adaptive profiles consistent throughout,
defined a 199-replicate equal-emission bootstrap, reclassified permuted arrival
as an alignment stress, specified predictive warning statistics and silent
misspecification rules, froze all enum and JSON domains, defined `source_sha256`,
and kept both holdout receipts immutable. No implementation began during these
packet review iterations.

A fourth re-review identified residual protocol detail: the runbook's physical
order still placed holdout before pre-holdout validation, final tracked-state
verification was not repeated immediately before commit, equal-emission and
arrival-permutation aggregation remained open, predictive Monte Carlo warnings
lacked a draw namespace, and several schema domains remained implicit.

The fourth correction physically reordered the runbook, repeated all state
guards before commit, fixed a pooled 24-replicate equal-emission test with 199
bootstrap bundles, fixed half-block arrival permutation and correlation audit,
fixed 199 predictive reference draws per replicate/stratum, expanded control
evidence fields, and closed enum plus nested JSON schemas.

## Task 0 - Authoritative Contract Freeze

The Task 0 writer transcribed the frozen Goal contract into the authoritative
spec and added the required structural- and practical-identifiability argument.
No simulator, tests, dependencies, generated artifacts, calibration data, or
holdout material were created.

Recorded paths and SHA-256 values:

```text
spec/synth_medium_latent_response_observation_recovery_gate.md
265a6144cc0575b7ff7b89bc1bfba4f603484aaac62352f95024d1d06c1f08dc

docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
d41037f5a3b4ada691f2880730b5e91fdc375b62eadfc35ab4bd1d6a9e1074c2
```

First-pass canonical source digests:

```text
landscape_sha256=53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a
arrival_sha256=5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba
```

The first-pass source reconciliation reproduced `6048` landscape cells,
`5225` passable cells, `823` water cells, `4605` final predator-colonised
passable cells, and `4289` finite Goal 018 prey quasi-extirpations. The
pre-simulation practical design audit over all passable cells and potential
six-unit transition intervals from `6` through `120` returned rank `3` and
condition number `1.99026083038`, below the frozen `1e8` stop threshold.

Exact first-pass source-serialization and design-audit command:

```bash
uv run python - <<'PY'
from __future__ import annotations

import csv
import hashlib
import io
import math

import numpy as np

from spatext.synth.medium.landscape import build_synth_medium_landscape
from spatext.synth.medium.spread_impact import build_synth_medium_spread_impact_review_pack


def canonical_csv(header: tuple[str, ...], rows: list[tuple[object, ...]]) -> bytes:
    buffer = io.StringIO(newline="")
    output = csv.writer(buffer, lineterminator="\n")
    output.writerow(header)
    output.writerows(rows)
    return buffer.getvalue().encode("utf-8")


landscape = build_synth_medium_landscape()
spread = build_synth_medium_spread_impact_review_pack()
cells = sorted(landscape.cells, key=lambda cell: int(cell.cell_id))
truth = sorted(spread.cell_truth_rows, key=lambda row: int(row.landscape_cell.cell_id))

landscape_bytes = canonical_csv(
    ("cell_id", "row", "col", "passability", "habitat_class", "quality"),
    [
        (
            int(cell.cell_id),
            int(cell.row),
            int(cell.col),
            cell.passability,
            cell.habitat_class,
            format(cell.quality, ".12g"),
        )
        for cell in cells
    ],
)
arrival_bytes = canonical_csv(
    ("cell_id", "predator_arrival_time"),
    [
        (
            int(row.landscape_cell.cell_id),
            ""
            if row.predator_arrival_time is None
            or not math.isfinite(row.predator_arrival_time)
            else format(row.predator_arrival_time, ".12g"),
        )
        for row in truth
    ],
)

passable = [row for row in truth if row.landscape_cell.passability == "passable"]
water = [row for row in truth if row.landscape_cell.passability == "water"]
colonized = [row for row in passable if row.predator_final_occupied]
extirpated = [row for row in passable if row.prey_extirpation_time is not None]

quality = np.asarray([row.landscape_cell.quality for row in passable], dtype=float)
q_standardized = (quality - quality.mean()) / quality.std(ddof=0)
design_rows: list[tuple[float, float, float]] = []
for row, q_value in zip(passable, q_standardized, strict=True):
    arrival = row.predator_arrival_time
    for time in range(6, 121, 6):
        g_value = 0.0 if arrival is None or not math.isfinite(arrival) else max((time - arrival) / 30.0, 0.0)
        design_rows.append((1.0, g_value, float(q_value)))
design = np.asarray(design_rows, dtype=float)

print(f"landscape_sha256={hashlib.sha256(landscape_bytes).hexdigest()}")
print(f"arrival_sha256={hashlib.sha256(arrival_bytes).hexdigest()}")
print(f"landscape_bytes={len(landscape_bytes)}")
print(f"arrival_bytes={len(arrival_bytes)}")
print(f"landscape_rows={len(cells)}")
print(f"passable_rows={len(passable)}")
print(f"water_rows={len(water)}")
print(f"colonized_passable_rows={len(colonized)}")
print(f"finite_prey_extirpation_rows={len(extirpated)}")
print(f"design_rows={design.shape[0]}")
print(f"design_rank={np.linalg.matrix_rank(design)}")
print(f"design_condition_number={np.linalg.cond(design):.12g}")
PY
```

Exact hash and receipt-parsing commands:

```bash
shasum -a 256 spec/synth_medium_latent_response_observation_recovery_gate.md
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
uv run python -m json.tool docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json >/dev/null
```

Status: pending independent scientific and source-digest review. The receipt's
independent-check fields currently repeat the Task 0 writer's first-pass values
and `passed` remains `false`; they are not evidence of an independent
recomputation. Task 0 is therefore not independently approved or frozen for
implementation yet.

### Independent ACCEPT And Task 0 Freeze

The independent scientific and source-digest review returned `ACCEPT`. The
reviewer compared `626` frozen contract lines and found `0` diff lines. The
independent source reconstruction reproduced the required counts in order:
`6048` landscape cells, `5225` passable cells, `823` water cells, `4605` final
predator-colonised passable cells, and `4289` finite Goal 018 prey
quasi-extirpations.

The independent practical design audit returned rank `3` and condition number
`1.99026083038`. All targeted checks passed (`14/14`). The independent command
did not reuse `Log.md` as source evidence.

Final frozen hashes:

```text
spec/synth_medium_latent_response_observation_recovery_gate.md
265a6144cc0575b7ff7b89bc1bfba4f603484aaac62352f95024d1d06c1f08dc

docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb
```

Seal validation commands:

```bash
uv run python -m json.tool docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json >/dev/null
shasum -a 256 spec/synth_medium_latent_response_observation_recovery_gate.md
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
git diff --check
```

Task 0 is frozen and independently approved for Task 1. No simulation,
calibration, or holdout material was created.

## Task 1 - Observation Kernel

Implementation complete under strict red-green TDD; independent
spec-compliance and numerical-quality review remains pending.

### Behaviors And Tests

- `OBS-001`: frozen ordered effective rates and state-specific rate selection;
- `OBS-002`: zero-count Poisson log probability;
- `OBS-003`: positive-count Poisson log probability;
- `OBS-004`: effort-scaled state-specific means;
- `OBS-005`: composed state/effort/count log probability;
- `OBS-006`: finite positive ordered rate validation;
- `OBS-007`: finite positive effort validation;
- `OBS-008`: integral nonnegative count validation, including boolean rejection;
- `OBS-009`: finite positive Poisson mean validation;
- `OBS-010`: integer latent-state `0|1` validation, including boolean rejection;
- `OBS-011`: stable log probability at the frozen lower rate boundaries and
  very small positive effort; and
- `OBS-012`: reusable observation-kernel import boundary with no
  `spatext.synth` import.

The test file was written and hashed before production implementation:

```text
37baab4fc186861d3fc178cca40860d8714301ae72fbdd11d58c94ff93c20403  tests/test_observe.py
```

### RED

Exact command:

```bash
uv run pytest tests/test_observe.py --no-cov
```

Expected failure:

```text
collected 0 items / 1 error
E   ModuleNotFoundError: No module named 'spatext.observe'
ERROR tests/test_observe.py
1 error in 0.09s
```

Exit status: `2`. The failure was caused by the deliberately absent production
module, not by a test typo or an existing behavior.

### Dependency And Implementation

Exact dependency command:

```bash
uv add 'scipy>=1.17,<2'
```

The command updated only `pyproject.toml` and `uv.lock` for the new runtime
dependency, resolved `29` packages, and installed `scipy==1.18.0` on this
Python 3.14 environment.

Implementation paths:

```text
src/spatext/observe.py
pyproject.toml
uv.lock
```

The reusable API is a frozen `EffectiveCountRates` dataclass plus scalar
`state_rate`, `effort_scaled_mean`, `poisson_log_probability`, and
`state_count_log_probability` functions. The module uses
`scipy.special.gammaln` only for the positive-count factorial term and contains
no simulator, scenario, seed, benchmark, artifact, calibration, or holdout
policy.

### GREEN And Static Validation

Focused GREEN command and final result:

```bash
uv run pytest tests/test_observe.py --no-cov
```

```text
collected 32 items
tests/test_observe.py ................................                   [100%]
32 passed in 0.13s
```

Formatting and lint commands and results:

```bash
uv run ruff format tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
```

```text
2 files left unchanged
All checks passed!
```

The first strict type-check command exposed SciPy's missing `py.typed` marker:

```bash
uv run mypy src tests
```

```text
src/spatext/observe.py:6: error: Library stubs not installed for "scipy.special"  [import-untyped]
Found 1 error in 1 file (checked 57 source files)
```

Exit status: `1`. A direct environment check confirmed
`.venv/lib/python3.14/site-packages/scipy/py.typed` was absent. Because the
frozen dependency boundary permits only SciPy, the correction was one
import-local `# type: ignore[import-untyped]`, preserving strict checks for the
rest of the repository without adding a stub dependency. The exact rerun was:

```bash
uv run mypy src tests
```

```text
Success: no issues found in 57 source files
```

Final combined validation commands:

```bash
uv run pytest tests/test_observe.py --no-cov
uv run ruff format --check tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
uv run mypy src tests
uv lock --check
git diff --check
```

All exited `0`; the focused suite reported `32 passed`, both Python files were
already formatted, ruff and mypy were clean, the lock resolved `29` packages,
and `git diff --check` produced no output.

Final Task 1 file hashes before this append-only log update:

```text
37baab4fc186861d3fc178cca40860d8714301ae72fbdd11d58c94ff93c20403  tests/test_observe.py
e3720d534059449700e5e72ae742315aca6c2f5e373fe2851b11562624521ca0  src/spatext/observe.py
dc3c8602e90d1b3c0f3bceb12dd835ee98d083c625228dd2139dcee450d91f12  pyproject.toml
3ddc2092eb82b014263217a6a800d4c67e7c3702c1bd738a92a6b862e623eebe  uv.lock
```

### Self-Review

Self-review found the implementation aligned with the frozen observation
equations and Task 1 boundary: state `0` selects `lambda_present`, state `1`
selects `lambda_quasi`, known effort scales the effective rate once, and the
Poisson log probability is the only likelihood. Invalid inputs fail with named
`ValueError` messages, and the zero-count branch avoids an unnecessary
`0 * log(mean)` operation.

The dependency diff adds only `scipy>=1.17,<2`; the frozen spec remains at
`265a6144cc0575b7ff7b89bc1bfba4f603484aaac62352f95024d1d06c1f08dc`
and the approved source receipt remains at
`5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`.
No independent review is claimed. No Task 2 work, artifacts, simulations,
calibration rows, seeds, or holdout material were created.

### Review Fix Cycle 2 - Representability Boundary

Task 1 review identified two important numerical findings and one minor test
quality finding:

1. accepted very large count/mean inputs could suffer cancellation or raise
   `OverflowError` in arithmetic libraries;
2. separately valid effort and rate inputs could multiply to zero or infinity;
   and
3. the import-boundary test did not detect `from spatext import synth`.

The accepted resolution was conservative explicit rejection, not approximate
huge-count arithmetic. Tests `OBS-013` through `OBS-016` cover an oversized
count, oversized direct mean, overflowed effort-rate product, and underflowed
subnormal effort-rate product. `OBS-012` now proves its AST rule detects
`from spatext import synth`, `from spatext.synth import medium`, and
`import spatext.synth.medium`.

The changed test file was hashed before the second-cycle source edit:

```text
d931194a25e8389d778595309848a8b3d4ee66f2b171f4185e0a7a4f175c93de  tests/test_observe.py
```

Second-cycle RED command:

```bash
uv run pytest tests/test_observe.py --no-cov
```

Exact RED result:

```text
collected 36 items
tests/test_observe.py ................................FFFF               [100%]
FAILED test_obs_013_poisson_log_probability_rejects_unrepresentable_count
FAILED test_obs_014_poisson_log_probability_rejects_unrepresentable_mean
FAILED test_obs_015_effort_scaled_mean_rejects_overflowed_product
FAILED test_obs_016_effort_scaled_mean_rejects_underflowed_product
4 failed, 32 passed in 0.15s
```

Each failure was `Failed: DID NOT RAISE <class 'ValueError'>`; exit status was
`1`. The pre-existing 32 cases remained green, and the four failures directly
demonstrated the missing review behavior before the source change.

The implementation added one private documented shared boundary:

```text
_REPRESENTABILITY_LIMIT = 1_000_000_000
```

`count` and direct `mean` values above the limit now raise `ValueError`.
`effort_scaled_mean` validates its computed product after multiplication and
raises `ValueError` unless the result is finite, positive, and no greater than
the same limit. The boundary is far above all frozen Goal 023 count and mean
ranges. No dependency change was required.

Second-cycle GREEN command and result:

```bash
uv run pytest tests/test_observe.py --no-cov
```

```text
collected 36 items
tests/test_observe.py ....................................               [100%]
36 passed in 0.13s
```

Static validation commands:

```bash
uv run ruff format tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
uv run mypy src tests
git diff --check
```

All exited `0`: ruff reported `2 files left unchanged` and
`All checks passed!`; mypy reported `Success: no issues found in 57 source
files`; `git diff --check` produced no output.

Final second-cycle file hashes before this append-only log update:

```text
d931194a25e8389d778595309848a8b3d4ee66f2b171f4185e0a7a4f175c93de  tests/test_observe.py
87576da8d516420cbb2ad31bd84da31bd3cf203141ec66dc132bccf3965b7cdb  src/spatext/observe.py
dc3c8602e90d1b3c0f3bceb12dd835ee98d083c625228dd2139dcee450d91f12  pyproject.toml
3ddc2092eb82b014263217a6a800d4c67e7c3702c1bd738a92a6b862e623eebe  uv.lock
```

Reviewer-finding disposition: all three findings are implemented and covered
by the second-cycle focused suite. Independent re-review is not claimed and
remains pending. No Task 2 work, commit, push, artifact, simulation, calibration
row, seed, or holdout material was created.

### Review Fix Cycle 3 - Oversized Integers And Accepted Boundary Stability

A narrow follow-up review required controlled rejection before float
conversion for oversized Python integers and a stable result at the accepted
representability boundary. Tests `OBS-017` through `OBS-020` cover
`mean=10**400`, `effort=10**400`, each rate set to `10**400`, and
`count=mean=1_000_000_000`.

For the accepted boundary, the test reference is

```text
-0.5 * log(2 * pi * count) - 1 / (12 * count)
```

with absolute tolerance `1e-12`. The first omitted Stirling term at
`count=10**9` is `1 / (360 * count**3)`, below `3e-30`; the tolerance therefore
comfortably covers floating-point rounding without accepting the observed
cancellation error.

The changed test file was hashed before the third-cycle source edit:

```text
00861f0145b87ee47a651586d29cb21525be3cc300dff4a66ea5accac68bcb67  tests/test_observe.py
```

Third-cycle RED command:

```bash
uv run pytest tests/test_observe.py --no-cov
```

Exact RED result:

```text
collected 41 items
tests/test_observe.py ....................................FFFFF          [100%]
FAILED test_obs_017_oversized_python_integer_mean_raises_value_error
FAILED test_obs_018_oversized_python_integer_effort_raises_value_error
FAILED test_obs_019_oversized_python_integer_rate_raises_value_error[lambda_present]
FAILED test_obs_019_oversized_python_integer_rate_raises_value_error[lambda_quasi]
FAILED test_obs_020_representability_limit_is_accepted_with_stable_log_probability
5 failed, 36 passed in 0.15s
```

The four oversized-integer cases raised
`OverflowError: int too large to convert to float` from `math.isfinite` instead
of controlled `ValueError`. The accepted-boundary calculation was finite but
returned `-11.280570983886719` rather than the stable reference
`-11.28057145176121`, an absolute cancellation error of approximately
`4.68e-7`. Exit status was `1`.

The implementation now branches on Python integers before calling
`math.isfinite`. An oversized integer `mean` is compared directly with the
shared `1_000_000_000` mean limit; oversized integer effort or rates are
rejected as not finite-positive float-representable inputs before conversion.
Boolean rejection and all existing error messages and limits are preserved.

Ordinary Goal 023 counts retain the exact `scipy.special.gammaln` path. For
counts at least `10_000` with mean within 50% of count, a stable local form uses
the Poisson deviance, a cancellation-safe `delta - log1p(delta)` series near
zero, and Stirling corrections through order `count**-7`. Values above the
conservative representability limit remain rejected rather than approximated.

Third-cycle GREEN command and result:

```bash
uv run pytest tests/test_observe.py --no-cov
```

```text
collected 41 items
tests/test_observe.py .........................................          [100%]
41 passed in 0.13s
```

Static and post-format GREEN commands:

```bash
uv run ruff format tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
uv run mypy src tests
git diff --check
uv run pytest tests/test_observe.py --no-cov
```

All exited `0`. Ruff reformatted one file and then reported
`All checks passed!`; mypy reported `Success: no issues found in 57 source
files`; `git diff --check` produced no output; the post-format focused rerun
reported `41 passed in 0.13s`.

Final third-cycle hashes before this append-only log update:

```text
00861f0145b87ee47a651586d29cb21525be3cc300dff4a66ea5accac68bcb67  tests/test_observe.py
2ecddf311bbd9a2cadfee04503e7c6381961c75bdcf0e91c8844556f3de25859  src/spatext/observe.py
dc3c8602e90d1b3c0f3bceb12dd835ee98d083c625228dd2139dcee450d91f12  pyproject.toml
3ddc2092eb82b014263217a6a800d4c67e7c3702c1bd738a92a6b862e623eebe  uv.lock
```

Reviewer-finding disposition: all third-cycle findings are implemented and
covered by focused tests. No dependency, frozen spec, receipt, Task 2, commit,
push, artifact, simulation, calibration, seed, or holdout change was made.

## Task 2 - Latent Transition Likelihood

Pending.

## Task 3 - Replicated Recovery And Controls

Pending.

## Task 4 - Artifact Contract And Documentation

Pending.

## Independent Reviews

Pending.

## Final Validation And Publication

Pending.

## 2026-07-11 - Pre-Simulation Contract Amendment Baseline

The pre-amendment evidence file was verified before any contract edit:

```text
1b5cb946d3340c61c6b4021231a847ed5406809f144c62baf6a228cd9fb0850b  /tmp/spatext-goal023-pre-amendment-evidence.txt
```

Its contents are appended verbatim:

```text
utc=2026-07-11T02:12:57Z
branch=codex/spatext-goal023-latent-response-observation-gate
head=53462d0365babf2c8070714a930f69b4071af276
origin_main=53462d0365babf2c8070714a930f69b4071af276
--- status ---
 M pyproject.toml
 M uv.lock
?? docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
?? docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md
?? docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
?? docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
?? docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
?? spec/synth_medium_latent_response_observation_recovery_gate.md
?? src/spatext/observe.py
?? tests/test_observe.py
--- modified tracked ---
pyproject.toml
uv.lock
--- staged ---
--- untracked ---
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
spec/synth_medium_latent_response_observation_recovery_gate.md
src/spatext/observe.py
tests/test_observe.py
--- frozen hashes ---
265a6144cc0575b7ff7b89bc1bfba4f603484aaac62352f95024d1d06c1f08dc  spec/synth_medium_latent_response_observation_recovery_gate.md
5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
--- prohibited material search ---
--- goal023 ignored artifact status ---
```

The frozen specification hash
`265a6144cc0575b7ff7b89bc1bfba4f603484aaac62352f95024d1d06c1f08dc`
is now classified `superseded_pre_simulation`. This status supplements rather
than rewrites the original Task 0 freeze entry.

At this amendment boundary, no Task 2 source or test file, simulation, seed
namespace, calibration, Goal 023 artifact, `preholdout_state_receipt.json`, or
holdout exposure existed.

## 2026-07-11 - Replacement Contract Written, Reviews Pending

The controlled amendment changed only Goal 023 `Goal.md`, `Plan.md`,
`Runbook.md`, `Log.md`, and the authoritative spec. It preserved every
estimand, support, generating value, all eleven scenarios, master seed,
replication count, threshold, recommendation precedence, artifact contract,
boundary, and publication-authority clause.

Replacement contract hashes:

```text
2ed0c6eb9c63e84b0542acc4b0c6e169848fe10b39b1e0633601177175d64bbd  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
017086d71b2bed066869c26ec1949dc3ccde09bdbc9661d92853fff686908c21  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
8806946399573a070289a1917803f49c2af2da8a8d091e39bdde3a29df0dd19f  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
6a7ab98098a51aab5e41252629fca70e89ebd36ffac93f98d10326fefa1bd169  spec/synth_medium_latent_response_observation_recovery_gate.md
```

The source digest receipt was not edited and remains:

```text
5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
```

The two frozen non-holdout RNG vectors were computed from compact sorted-key
ASCII JSON using SHA-256, eight big-endian `uint32` entropy words,
`SeedSequence`, `PCG64DXSM`, and `bit_generator.random_raw(3)`. Exact command:

```bash
uv run python - <<'PY'
import hashlib
import json

import numpy as np

vectors = (
    {
        "goal": "023",
        "master_seed": 20260711,
        "scenario_id": "dense_count_exact_model",
        "split": "development",
        "replicate_index": 0,
        "component": "process",
        "draw_index": None,
    },
    {
        "goal": "023",
        "master_seed": 20260711,
        "scenario_id": "structured_imperfect_effort",
        "split": "calibration",
        "replicate_index": 7,
        "component": "predictive_reference",
        "draw_index": 0,
    },
)
for payload in vectors:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(canonical.encode("utf-8")).digest()
    words = [int.from_bytes(digest[index:index + 4], "big") for index in range(0, 32, 4)]
    rng = np.random.Generator(np.random.PCG64DXSM(np.random.SeedSequence(words)))
    draws = [int(value) for value in rng.bit_generator.random_raw(3)]
    print(canonical)
    print(hashlib.sha256(canonical.encode("utf-8")).hexdigest())
    print(words)
    print(draws)
PY
```

No holdout payload was instantiated. The exact vector payloads, hashes,
entropy words, and first three raw `uint64` draws are frozen in Goal and spec.

Markdown and diff hygiene commands:

```bash
uv run pre-commit run trailing-whitespace --files docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md spec/synth_medium_latent_response_observation_recovery_gate.md
uv run pre-commit run end-of-file-fixer --files docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md spec/synth_medium_latent_response_observation_recovery_gate.md
git diff --check
```

Both document hooks passed and `git diff --check` returned zero with no output.
The Goal/spec comparison had zero contract diff lines; its only diff was the
spec title and amendment preface.

Exact hash and absence/status commands:

```bash
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md spec/synth_medium_latent_response_observation_recovery_gate.md docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
test ! -e tests/test_synth_medium_latent_response_observation_recovery.py
test ! -e src/spatext/synth/medium/latent_response_observation_recovery.py
test ! -d artifacts/synth_medium_latent_response_observation_recovery
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
git status --short --branch --untracked-files=all
```

All hash and absence commands exited zero. Status remained on
`codex/spatext-goal023-latent-response-observation-gate` with no staged files;
the pre-existing Task 1 dependency/source/test and Goal 023 packet footprint
remained present.

Non-mutating Task 1 recheck:

```bash
uv run pytest tests/test_observe.py --no-cov
uv run ruff format --check tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
uv run mypy src tests
```

Results were `41 passed in 0.20s`, `2 files already formatted`,
`All checks passed!`, and `Success: no issues found in 57 source files`.

Amendment review status:

```text
Task 1 terminology/API red-green polish: PENDING
Task 1 fresh independent re-review: PENDING
independent scientific-identifiability review: PENDING
independent executor-readiness review: PENDING
independent provenance/freeze review: PENDING
```

The replacement documents are written but not independently sealed. Task 2
remains stopped. No Task 2 files, simulation, seed namespace, calibration,
Goal 023 artifact, preholdout receipt, holdout exposure, staging, commit, push,
or remote compute occurred.

## 2026-07-11 - Task 1 Numerical-Domain Terminology/API Polish

This fresh red-green cycle implemented the amended pre-simulation distinction
between scientific-input validation and observation-kernel computational-domain
failure. It changed only `tests/test_observe.py`, `src/spatext/observe.py`, and
this append-only log.

Behavior coverage added or strengthened:

- `OBS-006` through `OBS-010`: ordinary invalid rates, effort, counts, means,
  and states remain exact `ValueError`, including bool/NaN/Inf cases;
- `OBS-013` through `OBS-019`: count/mean limit violations, float-domain
  effort/rate overflow, and effort-rate underflow/overflow raise the dedicated
  numerical-domain exception with computational-domain terminology;
- `OBS-020`: the accepted billion boundary retains its stable value;
- `OBS-021`: public `NumericalDomainError` subclasses `ValueError`;
- `OBS-022`: invalid scientific parameters are not numerical-domain errors;
- `OBS-023`: numerical-domain failures raise rather than returning `-inf`, zero
  probability, or another sentinel;
- `OBS-024`: test-local frozen contract values prove
  `1.3 * 10.0 = 13.0`, with the `1_000_000_000` computational mean limit more
  than six orders of magnitude higher; and
- `OBS-025`: source uses `_COMPUTATIONAL_DOMAIN_LIMIT` and contains no old
  representability terminology.

The test file was hashed before the production edit:

```text
3ea3caeb69da6690b1a416d4f0b7127f2db895cf589c0a2dd4ced20f0a0b0617  tests/test_observe.py
```

Exact RED command:

```bash
uv run pytest tests/test_observe.py --no-cov
```

Exact RED result:

```text
collected 46 items
tests/test_observe.py ................................FFFFFFFF.F.F.F     [100%]
11 failed, 35 passed in 0.19s
```

Failing IDs were `OBS-013` through `OBS-019`, `OBS-021`, `OBS-023`, and
`OBS-025`. Assertions showed the missing public exception, old
`representability` messages and constant, and ordinary `ValueError` being used
for implementation-domain failures. Exit status was `1`. The 35 unaffected
scientific and numerical-result cases remained green.

The minimal implementation:

- added public typed `NumericalDomainError(ValueError)`;
- renamed `_REPRESENTABILITY_LIMIT` to `_COMPUTATIONAL_DOMAIN_LIMIT`;
- changed implementation-limit guard messages to explicit
  computational-domain language;
- raises `NumericalDomainError` only for count/direct-mean values above
  `1_000_000_000`, effort/rate integers too large for float-domain conversion,
  or effort-rate products that underflow, overflow, or exceed the limit; and
- preserves ordinary exact `ValueError` for invalid zero, negative, bool,
  NaN/Inf, state, count-schema, and rate-ordering inputs.

The exception remains catchable as `ValueError`. No probability sentinel is
returned, no benchmark policy entered `observe.py`, and the unbounded Poisson
statistical support was not truncated, censored, zero-mass adjusted, or
renormalised.

Exact focused GREEN command and result:

```bash
uv run pytest tests/test_observe.py --no-cov
```

```text
collected 46 items
tests/test_observe.py ..............................................     [100%]
46 passed in 0.15s
```

Static commands and results:

```bash
uv run ruff format tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
uv run mypy src tests
git diff --check
```

Ruff reformatted one file and then reported `All checks passed!`; mypy reported
`Success: no issues found in 57 source files`; `git diff --check` returned zero
with no output. The post-format focused rerun again reported `46 passed in
0.15s`.

Relevant regression command:

```bash
uv run pytest tests/test_synth_small_observations.py tests/test_synth_medium_observation_design.py tests/test_synth_medium_recoverability_target_observation_design.py --no-cov
```

Result: `17 passed in 44.03s`.

Final Task 1 polish hashes before this append-only log update:

```text
4a4906e30e5fd996e6a7ea90a6ae4108f04add1b7412d92ddd685d383f996b73  tests/test_observe.py
28faa9c34d7ee1e8354901e6c6fbd6991fc072902ec1c7b0a32306b335e28350  src/spatext/observe.py
```

Unchanged authority/dependency hashes:

```text
dc3c8602e90d1b3c0f3bceb12dd835ee98d083c625228dd2139dcee450d91f12  pyproject.toml
3ddc2092eb82b014263217a6a800d4c67e7c3702c1bd738a92a6b862e623eebe  uv.lock
2ed0c6eb9c63e84b0542acc4b0c6e169848fe10b39b1e0633601177175d64bbd  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
017086d71b2bed066869c26ec1949dc3ccde09bdbc9661d92853fff686908c21  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
8806946399573a070289a1917803f49c2af2da8a8d091e39bdde3a29df0dd19f  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
6a7ab98098a51aab5e41252629fca70e89ebd36ffac93f98d10326fefa1bd169  spec/synth_medium_latent_response_observation_recovery_gate.md
5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
```

Task 1 terminology/API polish implementation status: `COMPLETE`.
Fresh independent Task 1 re-review status: `PENDING`. Task 2 remains stopped;
no Task 2 file, seed, artifact, simulation, calibration, holdout, staging,
commit, push, or remote-compute work occurred.

## 2026-07-11 - Task 1 Integer-Product Domain Review Fix

An important review reproducer showed that separately accepted integer effort
and rate values could produce an integer product too large for
`math.isfinite`, leaking `OverflowError` before the computational-domain guard:

```python
rates = EffectiveCountRates(lambda_present=10**308, lambda_quasi=1)
effort_scaled_mean(effort=10, state=0, rates=rates)
```

Tests `OBS-026` and `OBS-027` were added before the source change. They require
the exact reproducer to raise `NumericalDomainError` and require a valid
in-domain integer product to return a `float`.

Pre-implementation test hash and exact RED command:

```text
842908091c6a19f306db91cfef9f9c3d2f07eeb6062003c713fc0e4d5fc17309  tests/test_observe.py
```

```bash
uv run pytest tests/test_observe.py --no-cov
```

Exact RED result:

```text
collected 48 items
tests/test_observe.py ..............................................FF   [100%]
FAILED test_obs_026_integer_product_above_float_domain_raises_numerical_domain_error
E   OverflowError: int too large to convert to float
FAILED test_obs_027_valid_integer_product_is_returned_as_float
E   AssertionError: assert <class 'int'> is float
2 failed, 46 passed in 0.15s
```

Exit status was `1`. The two failures exactly isolated the review finding; all
46 prior observation-kernel tests remained green.

The minimal source fix checks an integer effort-rate product against
`_COMPUTATIONAL_DOMAIN_LIMIT` before `math.isfinite` or float conversion. A
product above the limit raises `NumericalDomainError` with the existing
computational-domain message. An accepted integer product is converted to
`float` before return. Ordinary outputs, validation types, rate ordering, and
the statistical Poisson law are otherwise unchanged.

Exact focused GREEN command and result:

```bash
uv run pytest tests/test_observe.py --no-cov
```

```text
collected 48 items
tests/test_observe.py ................................................   [100%]
48 passed in 0.14s
```

Static, lock, and diff commands:

```bash
uv run ruff format tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
uv run mypy src tests
uv lock --check
git diff --check
```

All exited `0`: both files were already formatted, ruff passed, mypy reported
no issues in 57 source files, the lock resolved 29 packages, and
`git diff --check` produced no output.

Relevant regression command and result:

```bash
uv run pytest tests/test_synth_small_observations.py tests/test_synth_medium_observation_design.py tests/test_synth_medium_recoverability_target_observation_design.py --no-cov
```

Result: `17 passed in 44.51s`.

Final review-fix hashes before this append-only log update:

```text
842908091c6a19f306db91cfef9f9c3d2f07eeb6062003c713fc0e4d5fc17309  tests/test_observe.py
cfefe7ee14f0d9221fa73d96691c7b1657adbefa2f87f756c82c7019be73b74f  src/spatext/observe.py
```

## 2026-07-11 - Final Narrow Contract Correction Seal

The narrow scientific/executor findings are addressed in the replacement
documents, pending fresh independent review:

```text
tolerance frontier: ADDRESSED_PENDING_REVIEW
  Target recovery is RMSE <= 5e-5 with scaled maximum natural-parameter
  distance < 0.01. Collision is RMSE <= 5e-5 with distance >= 0.01. The
  >=12/16 optimizer-success gate, objective, starts, options, rank, and
  condition rules are unchanged.
  All nine dry audits are frozen as pre-estimation tests. Exact recovery counts
  are dense A/B/C 16/15/2, structured 16/14/3, and sparse 15/16/16, with no
  collision. The pair 5e-5/0.01 is the unique passing candidate in
  {5e-5,1e-4,2e-4} x {0.0025,0.005,0.01}. Distance 0.01 means numerical
  equivalence within 1% of natural support width and is supporting
  noncollision evidence only.
equal-emission scientific status: ADDRESSED_PENDING_REVIEW
  Structural labels are independent of bootstrap p. lambda_present remains
  structurally identified from known-present t0 emissions and has practical
  status not_applicable because no profile is computed. lambda_equal is
  structurally and practically identified subject to a finite interior MLE.
  alpha, beta_driver, beta_quality, and lambda_quasi are structurally and
  practically unidentified. The ordered emission contrast is unidentifiable;
  the lambda_present baseline level is not. The gate still requires p >= 0.05
  and all 199 ordered refits; failure changes the gate, never structural labels.
```

The prior scientific and provenance `ACCEPT` decisions remain preserved only
for the preceding document tuple. They are non-transferable to these hashes.
Replacement contract hashes before this append-only Log update are:

```text
cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d  spec/synth_medium_latent_response_observation_recovery_gate.md
```

Exact document and semantic commands:

```bash
diff -u \
  <(sed -n '/^## Objective/,$p' docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md) \
  <(sed -n '/^## Objective/,$p' spec/synth_medium_latent_response_observation_recovery_gate.md)
uv run pre-commit run trailing-whitespace --files \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
uv run pre-commit run end-of-file-fixer --files \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
test "$(rg -c 'RMSE <= 5e-5' docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md)" = "2"
test "$(rg -c 'RMSE <= 5e-5' spec/synth_medium_latent_response_observation_recovery_gate.md)" = "2"
if rg -n 'RMSE <= (1e-5|1e-8)' \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md; then exit 1; fi
git diff --check
```

The Goal/spec body diff was empty, both document hooks passed, exactly two
`RMSE <= 5e-5` rules occurred in each contract document, no superseded residual
rule remained, all nine-audit and equal-status semantic checks passed, and
`git diff --check` produced no output.

Hash-specific Task 1 commands and results:

```bash
uv run pytest tests/test_observe.py --no-cov
uv run ruff format --check tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
uv run mypy src tests
uv lock --check
```

Results were `48 passed`, two files already formatted, Ruff passed, mypy found
no issues in 57 source files, and the unchanged lock resolved 29 packages.
Task 1 `ACCEPT` remains hash-specific to:

```text
842908091c6a19f306db91cfef9f9c3d2f07eeb6062003c713fc0e4d5fc17309  tests/test_observe.py
cfefe7ee14f0d9221fa73d96691c7b1657adbefa2f87f756c82c7019be73b74f  src/spatext/observe.py
```

Receipt, absence, hash, and status commands:

```bash
test "$(shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json | awk '{print $1}')" = \
  "5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb"
test ! -e tests/test_synth_medium_latent_response_observation_recovery.py
test ! -e src/spatext/synth/medium/latent_response_observation_recovery.py
test ! -d artifacts/synth_medium_latent_response_observation_recovery
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
shasum -a 256 \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json \
  tests/test_observe.py src/spatext/observe.py
git status --short --branch --untracked-files=all
```

The source receipt remains unchanged at
`5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`.
All Task 2, artifact, receipt, and instantiated-holdout-payload absence checks
passed. Final review state is:

```text
Task 1 independent review: ACCEPT, unchanged hash-specific evidence
scientific-identifiability document re-review: PENDING
executor-readiness document re-review: PENDING
provenance/freeze document re-review: PENDING
```

Task 2 remains stopped until all three document re-reviews return `ACCEPT` with
no Critical or Important finding. No source, test, dependency, receipt, Task 2,
payload, artifact, seed, simulation, calibration, holdout, staging, commit, or
push edit or action occurred.

Dependency and amended authority hashes remained unchanged. Fresh independent
Task 1 re-review remains pending. No Goal/spec/Plan/Runbook/source-receipt,
Task 2, seed, artifact, calibration, holdout, staging, commit, or push change
occurred.

## 2026-07-11 - Amendment Iteration 1 Reviewer Dispositions

Read-only scientific and numerical review found amendment iteration 1
incomplete and returned `REVISE`. The unresolved Important findings concern
the numerical noncollision audit, design-diagnostic separation, stable process
primitives, exact optimizer/profile mechanics, stochastic consumption order,
holdout denominators, predictive warning calibration, literal artifact
schemas, and the runtime gate.

The amendment-1 contract hashes are preserved and now classified
`reviewed_not_accepted_pre_simulation`:

```text
2ed0c6eb9c63e84b0542acc4b0c6e169848fe10b39b1e0633601177175d64bbd  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
017086d71b2bed066869c26ec1949dc3ccde09bdbc9661d92853fff686908c21  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
8806946399573a070289a1917803f49c2af2da8a8d091e39bdde3a29df0dd19f  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
6a7ab98098a51aab5e41252629fca70e89ebd36ffac93f98d10326fefa1bd169  spec/synth_medium_latent_response_observation_recovery_gate.md
```

Reviewer dispositions:

```text
scientific-identifiability review: REVISE
numerical/executor-readiness review: REVISE
provenance/freeze review of amendment-1 state: ACCEPT, non-transferable
```

The current provenance `ACCEPT` applies only to the amendment-1 hashes. It must
be repeated after amendment iteration 2 changes any contract hash and does not
authorise Task 2. All iteration-2 fresh re-reviews are `PENDING`. Task 2 remains
stopped; no Task 2 file, simulation, seed namespace, calibration, artifact,
preholdout receipt, holdout exposure, staging, commit, or push exists.

## 2026-07-11 - Controlled Amendment Iteration 2 Seal Pending Review

Amendment iteration 2 addresses the read-only reviewers' Important findings
in the controlled document scope. These are writer dispositions only; they do
not constitute independent acceptance:

```text
A numerical noncollision audit: ADDRESSED_PENDING_REVIEW
  Exact canonical vector, float64 stable evaluation, scaled finite-difference
  Jacobian, SVD convention, 16-start inverse audit, executable/collision rules,
  and three literal rank-failing controls are frozen.
B design diagnostic separation: ADDRESSED_PENDING_REVIEW
  Potential, oracle-only truth-at-risk, and analyst plug-in gates now have
  distinct provenance and roles; truth-at-risk is excluded from every joint
  fitting and acceptance surface.
C stable numerical primitives: ADDRESSED_PENDING_REVIEW
  Float64 arrays, ddof=0 standardization, direct stable cloglog log primitives,
  support-extreme tests, and scipy.special.logsumexp are mandatory.
D optimizer/profile mechanics: ADDRESSED_PENDING_REVIEW
  The literal minimize call, rate maps, projection/deduplication, deterministic
  sorting, profile stepping/start/tie order, Brent rules, and invalidation rule
  are frozen.
E stochastic realization: ADDRESSED_PENDING_REVIEW
  Canonical sorting, complete RNG draws and consumption, component/index
  validation, fixed sparse/alignment frames, schedules, quintiles, permutation,
  PIT order, and future bootstrap mapping are frozen without seed realization.
F holdout denominators and deterministic gates: ADDRESSED_PENDING_REVIEW
  Attempted-replicate denominators, imputation, exact central-binomial sets,
  equal-emission refitting/bootstrap, predictive PIT/Holm/Stouffer rules, and
  literal replicate/summary schemas are frozen.
G runtime gate: ADDRESSED_PENDING_REVIEW
  Eight workers, a development/calibration-only representative benchmark,
  exact-count projections with 20% safety, 25-minute projection limits, a
  30-minute actual calibration limit, and stop/return-to-Barry behavior are
  frozen with timed Runbook commands.
H reviewer science finding: ADDRESSED_PENDING_REVIEW
  Every three-MCSE predictive warning rule is replaced by predictive-SD,
  Stouffer, randomized-PIT, and Holm rules; MCSE is accuracy reporting only;
  the oracle gate and all three audit fixtures are explicit.
```

The amendment-1 Goal, Plan, Runbook, and spec hashes remain classified
`reviewed_not_accepted_pre_simulation`; their preserved values are recorded in
the preceding entry. Replacement contract hashes are:

```text
f30d8b649a3dfd9592518b4fad0b190f9bb3602f8a10596da0b6c4497aba65f9  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
74f758b9349c4f4ce79c938a9903663718a4797f1b358aaab8fb2df4c8213991  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
3f1bc452f3a2f19669317da2b66dca178fdeb5c340af43a5cb907d9b516c0129  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
5105b843a659a62d265ee2b85951f6d89fa583a586b851968d333924c3a5146c  spec/synth_medium_latent_response_observation_recovery_gate.md
```

The independently accepted source digest receipt was not edited and remains:

```text
5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
```

Document/body and hygiene commands:

```bash
diff -u \
  <(sed -n '/^## Objective/,$p' docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md) \
  <(sed -n '/^## Objective/,$p' spec/synth_medium_latent_response_observation_recovery_gate.md)
uv run pre-commit run trailing-whitespace --files \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
uv run pre-commit run end-of-file-fixer --files \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
git diff --check
```

The contract-body diff was empty. Both document hooks passed and
`git diff --check` produced no output.

Nonmutating Task 1 commands and results:

```bash
uv run pytest tests/test_observe.py --no-cov
uv run ruff format --check tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
uv run mypy src tests
uv lock --check
uv run pytest tests/test_synth_small_observations.py \
  tests/test_synth_medium_observation_design.py \
  tests/test_synth_medium_recoverability_target_observation_design.py --no-cov
```

Results were `48 passed`, two files already formatted, Ruff passed, mypy found
no issues in 57 source files, the unchanged lock resolved 29 packages, and the
related observation regressions reported `17 passed`. Task 1 source and test
hashes remain:

```text
842908091c6a19f306db91cfef9f9c3d2f07eeb6062003c713fc0e4d5fc17309  tests/test_observe.py
cfefe7ee14f0d9221fa73d96691c7b1657adbefa2f87f756c82c7019be73b74f  src/spatext/observe.py
```

Seal and absence commands:

```bash
shasum -a 256 \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
test ! -e tests/test_synth_medium_latent_response_observation_recovery.py
test ! -e src/spatext/synth/medium/latent_response_observation_recovery.py
test ! -d artifacts/synth_medium_latent_response_observation_recovery
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
git status --short --branch --untracked-files=all
```

All absence checks passed. No Task 2 file, simulation, RNG payload/vector,
seed namespace, runtime benchmark, calibration, Goal 023 artifact,
preholdout receipt, holdout exposure, staging, commit, or push was created.

Fresh review status after these replacement hashes:

```text
Task 1 independent re-review: PENDING
scientific-identifiability review: PENDING
numerical/executor-readiness review: PENDING
provenance/freeze review: PENDING
```

The amendment-1 provenance `ACCEPT` must be repeated against these replacement
hashes. Task 2 remains stopped until every fresh review returns `ACCEPT` with
no Critical or Important finding.

## 2026-07-11 - Narrow Orchestrator Contract Correction Before Re-Review

The pre-correction amendment-2 documents had not received independent
acceptance. Their hashes are preserved here and classified
`corrected_before_re_review`:

```text
f30d8b649a3dfd9592518b4fad0b190f9bb3602f8a10596da0b6c4497aba65f9  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
74f758b9349c4f4ce79c938a9903663718a4797f1b358aaab8fb2df4c8213991  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
3f1bc452f3a2f19669317da2b66dca178fdeb5c340af43a5cb907d9b516c0129  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
5105b843a659a62d265ee2b85951f6d89fa583a586b851968d333924c3a5146c  spec/synth_medium_latent_response_observation_recovery_gate.md
```

Orchestrator correction dispositions are writer evidence only and remain
pending independent review:

```text
generalized SVD convention: CORRECTED_PENDING_REVIEW
  tol now uses max(n_rows,n_columns); full-column-rank condition evaluation is
  generic; the canonical audit explicitly uses five columns/rank 5 and every
  potential/oracle/plugin design diagnostic uses three columns/rank 3.
sparse honest coverage: CORRECTED_PENDING_REVIEW
  beta_driver uses all 24 attempted holdout replicates; failed, nonfinite,
  open, or missing intervals count false; the dedicated exact
  Binomial(24,0.90) acceptance set uses alpha 0.05 outside the 15 nested gates.
predictive failed-fit propagation: CORRECTED_PENDING_REVIEW
  any failed/nonfinite fit prevents predictive diagnostics and fails the
  scenario gate; attempted rows and denominators remain explicit and the
  literal predictive schemas represent unavailable diagnostics.
```

Final replacement contract hashes before this append-only Log update are:

```text
59a1199f60fd6cde702161e96cae31ab35d39ce3836e4edc237e4e56a39805e3  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
849976e4261dbc38c24f396c8a5413befd4d943c6652d20389f200df04f0f7d4  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
d6bf4cf09ce768b702a2e7e11e5ed6e9f4d0e602662d793721d7478923e1622d  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
6ad8a8033f1864bfe2fd94a36956cc0ab93147cd8a643f33d849e8e931e84386  spec/synth_medium_latent_response_observation_recovery_gate.md
```

The source digest receipt was not edited and remains:

```text
5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
```

Exact document and semantic checks:

```bash
diff -u \
  <(sed -n '/^## Objective/,$p' docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md) \
  <(sed -n '/^## Objective/,$p' spec/synth_medium_latent_response_observation_recovery_gate.md)
uv run pre-commit run trailing-whitespace --files \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
uv run pre-commit run end-of-file-fixer --files \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "max\(n_rows, n_columns\)|rank == n_columns|n_columns = 5|n_columns = 3" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
if rg -n "rank == 5 else infinity|max\(n_rows, 5\).*s_max|same SVD convention above" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md; then exit 1; fi
rg -n "24.*attempted holdout|n = 24.*p = 0.90|dedicated.*binomial acceptance" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "nonfinite fit prevents predictive|never silently omitted|failed_fit_count" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
git diff --check
```

The Goal/spec body diff was empty, both document hooks passed, every required
correction clause was present, forbidden five-column reuse wording was absent,
and `git diff --check` produced no output.

Exact receipt, absence, hash, and status commands:

```bash
test "$(shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json | awk '{print $1}')" = \
  "5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb"
test ! -e tests/test_synth_medium_latent_response_observation_recovery.py
test ! -e src/spatext/synth/medium/latent_response_observation_recovery.py
test ! -d artifacts/synth_medium_latent_response_observation_recovery
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
shasum -a 256 \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
git status --short --branch --untracked-files=all
```

The receipt and all absence checks passed. This correction edited documents
only. No source, test, dependency, receipt, Task 2, artifact, RNG payload,
seed, calibration, holdout, staging, commit, or push action occurred.

Fresh review status remains:

```text
Task 1 independent re-review: PENDING
scientific-identifiability review: PENDING
numerical/executor-readiness review: PENDING
provenance/freeze review: PENDING
```

Task 2 remains stopped until all required independent reviews return `ACCEPT`
with no Critical or Important finding.

## 2026-07-11 - Final Executor Review Findings Before Contract Fix

The final executor review applies to this pre-fix document hash tuple:

```text
59a1199f60fd6cde702161e96cae31ab35d39ce3836e4edc237e4e56a39805e3  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
849976e4261dbc38c24f396c8a5413befd4d943c6652d20389f200df04f0f7d4  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
d6bf4cf09ce768b702a2e7e11e5ed6e9f4d0e602662d793721d7478923e1622d  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
6ad8a8033f1864bfe2fd94a36956cc0ab93147cd8a643f33d849e8e931e84386  spec/synth_medium_latent_response_observation_recovery_gate.md
```

Executor disposition: `REVISE`. Final findings are:

```text
1. The 1e-8 target-recovery and collision RMSE thresholds are numerically
   infeasible. An independent sparse/A dry recomputation achieved 16/16
   successful searches, rank 5, condition 94.6757, and best RMSE 3.968e-6.
2. Equal-emission bootstrap outcomes do not yet map literally to structural
   and practical statuses for all five ordered parameters and lambda_equal.
3. Scenario, split, replicate, predictive-draw, and bootstrap index ranges are
   not completely frozen before RNG construction.
4. Predictive applicability, retained frames, permuted primary reference, and
   exact metric boundary behavior remain under-specified.
5. Sparse beta_driver median-width imputation and even-sample calculation are
   not literal.
6. Runtime timing units and eight-worker projection are not deterministically
   reproducible from the current runtime artifact.
7. Review statuses must be resealed by hash after these document changes.
```

The orchestrator confirms that Task 1 independent `ACCEPT` evidence is
hash-specific to the unchanged implementation files:

```text
842908091c6a19f306db91cfef9f9c3d2f07eeb6062003c713fc0e4d5fc17309  tests/test_observe.py
cfefe7ee14f0d9221fa73d96691c7b1657adbefa2f87f756c82c7019be73b74f  src/spatext/observe.py
Task 1 independent review: ACCEPT
```

The orchestrator also confirms scientific and provenance `ACCEPT` evidence on
the pre-fix document tuple above. Those decisions are preserved as
hash-specific and become non-transferable when any document hash changes.
They do not authorize Task 2 after this executor `REVISE`. The replacement
Goal, spec, Plan, and Runbook require fresh scientific, executor-readiness, and
provenance/freeze reviews, all initially `PENDING`.

## 2026-07-11 - Final Contract Review-Fix Dispositions And Seal

The final executor findings are addressed in the replacement documents, but
remain pending independent re-review:

```text
1. noncollision numerical feasibility: ADDRESSED_PENDING_REVIEW
   Both target-recovery and collision residual thresholds are RMSE <= 1e-5.
   The 12/16 success rule, 1e-3 scaled distance, objective, starts, and
   optimizer are unchanged. The contract records the independent sparse/A dry
   result: 16/16 successes, rank 5, condition 94.6757, best RMSE 3.968e-6.
   Tests must reproduce it before estimation; this is supporting evidence, not
   proof.
2. equal-emission classification: ADDRESSED_PENDING_REVIEW
   No profiles are allowed. Bootstrap p >= 0.05 plus all 199 successful
   ordered bundle refits assigns both statuses unidentified to the five
   ordered parameters and identified to lambda_equal. A smaller p or any
   failed refit forces model_contract_failed. Literal parameter-status rows
   encode the exact bootstrap decision.
3. replicate indices: ADDRESSED_PENDING_REVIEW
   All scientific scenario/split/replicate and predictive/bootstrap draw
   ranges are zero-based and literal. Unknown or out-of-range combinations
   fail before RNG construction. The timing-only equal-emission development
   exception is explicit and cannot emit scientific rows.
4. predictive applicability/frame/metrics: ADDRESSED_PENDING_REVIEW
   Process oracle is excluded; observation oracle is conditional-only; the
   eight standard-gate scenarios and equal-model diagnostic are explicit.
   Opportunity frames, schedules, efforts, masks, permuted primary reference,
   exact count metrics, n < 2 failure, and no-substitute failed-fit behavior
   are frozen.
5. sparse width: ADDRESSED_PENDING_REVIEW
   All 24 widths are used; failed/open/missing widths are imputed as 6; the
   ordinary median is the mean of ordered values 12 and 13 and is compared
   with the frozen structured 48-attempt imputed median.
6. deterministic runtime projection: ADDRESSED_PENDING_REVIEW
   Benchmark indices and the timing-only equal bundle are literal. Complete
   task units, repeated duration lists, 199 equal bootstrap copies,
   deterministic eight-worker LPT, 1.20 safety factor, 1500-second projections,
   1800-second calibration, and runtime_projection.json fields are frozen.
7. review status: ADDRESSED_PENDING_REVIEW
   Task 1 ACCEPT remains attached only to unchanged source/test hashes. Prior
   scientific and provenance ACCEPT decisions remain preserved but do not
   transfer to this replacement tuple. All three document reviews are PENDING.
```

Final replacement contract hashes before this append-only Log update are:

```text
52ba1eac6e84436019d29d0e52f481919dae0c83b0b18885b2941ce9bf03e5d4  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
a705928b1cb091454badd4d38f79b6b8371d55083743bcd45acb1754326d5f47  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
0f3a716a41baa5dccbc159af398d9be93586a07863322bc3630445ad18c14607  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
7f63cc30bc1bb2de260fc8ccea4c48ec9825ff3809922ee9612ae8e38dfab9d6  spec/synth_medium_latent_response_observation_recovery_gate.md
```

Goal/spec and document commands:

```bash
diff -u \
  <(sed -n '/^## Objective/,$p' docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md) \
  <(sed -n '/^## Objective/,$p' spec/synth_medium_latent_response_observation_recovery_gate.md)
uv run pre-commit run trailing-whitespace --files \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
uv run pre-commit run end-of-file-fixer --files \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
git diff --check
```

The Goal/spec contract-body diff was empty, both document hooks passed, all
semantic `rg` checks passed, obsolete `RMSE <= 1e-8` and runtime-benchmark
schema phrases were absent, and `git diff --check` produced no output.

Hash-specific nonmutating Task 1 commands:

```bash
uv run pytest tests/test_observe.py --no-cov
uv run ruff format --check tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
uv run mypy src tests
uv lock --check
```

Results were `48 passed`, two files already formatted, Ruff passed, mypy found
no issues in 57 source files, and the unchanged lock resolved 29 packages.
The accepted Task 1 hashes remain exact:

```text
842908091c6a19f306db91cfef9f9c3d2f07eeb6062003c713fc0e4d5fc17309  tests/test_observe.py
cfefe7ee14f0d9221fa73d96691c7b1657adbefa2f87f756c82c7019be73b74f  src/spatext/observe.py
Task 1 independent review: ACCEPT, hash-specific
```

Receipt, absence, hash, and status commands:

```bash
test "$(shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json | awk '{print $1}')" = \
  "5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb"
test ! -e tests/test_synth_medium_latent_response_observation_recovery.py
test ! -e src/spatext/synth/medium/latent_response_observation_recovery.py
test ! -d artifacts/synth_medium_latent_response_observation_recovery
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
shasum -a 256 \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json \
  tests/test_observe.py src/spatext/observe.py
git status --short --branch --untracked-files=all
```

The source receipt remains unchanged at
`5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`.
All Task 2, artifact, receipt, and instantiated-holdout-payload absence checks
passed.

Final review state for the replacement document tuple is:

```text
Task 1 independent review: ACCEPT, unchanged hash-specific evidence
scientific-identifiability document re-review: PENDING
executor-readiness document re-review: PENDING
provenance/freeze document re-review: PENDING
```

Task 2 remains stopped until all three document re-reviews return `ACCEPT` with
no Critical or Important finding. No source, test, dependency, receipt, Task 2,
artifact, seed, simulation, calibration, holdout, staging, commit, or push edit
or action occurred in this final contract review-fix iteration.

## 2026-07-11 - Final Narrow Science And Executor Findings

The prior final contract tuple was:

```text
52ba1eac6e84436019d29d0e52f481919dae0c83b0b18885b2941ce9bf03e5d4  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
a705928b1cb091454badd4d38f79b6b8371d55083743bcd45acb1754326d5f47  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
0f3a716a41baa5dccbc159af398d9be93586a07863322bc3630445ad18c14607  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
7f63cc30bc1bb2de260fc8ccea4c48ec9825ff3809922ee9612ae8e38dfab9d6  spec/synth_medium_latent_response_observation_recovery_gate.md
```

Scientific and provenance `ACCEPT` decisions attached to that exact tuple are
preserved as hash-specific. The subsequent narrow scientific/executor check
returned `REVISE` with two final findings:

```text
1. tolerance-frontier finding
   All nine dense/structured/sparse by A/B/C audits were executed over
   {5e-5,1e-4,2e-4} x {0.0025,0.005,0.01}. The unique passing candidate is
   residual 5e-5 and scaled distance 0.01. Recovery counts are dense 16/15/2,
   structured 16/14/3, and sparse 15/16/16; no collision was found.
2. equal-emission scientific-status finding
   Structural labels follow model degeneracy, not bootstrap p. Known-present
   t0 emissions retain structural identification of lambda_present even though
   the ordered lambda_present/lambda_quasi contrast is unidentifiable. The
   no-profile practical labels and equal-submodel lambda_equal labels require
   literal correction.
```

Tolerance-frontier disposition: `REVISE_CONTRACT`. The residual/distance pair
`5e-5/0.01` is the only tested pair that satisfies all nine audits. The distance
means numerical equivalence within 1% of natural support width and remains
supporting noncollision evidence only, not proof.

Editing the documents makes the prior scientific and provenance accepts
non-transferable. Fresh scientific-identifiability, executor-readiness, and
provenance/freeze reviews will be `PENDING` for the replacement tuple. Task 1
independent `ACCEPT` remains attached to its unchanged hashes:

```text
842908091c6a19f306db91cfef9f9c3d2f07eeb6062003c713fc0e4d5fc17309  tests/test_observe.py
cfefe7ee14f0d9221fa73d96691c7b1657adbefa2f87f756c82c7019be73b74f  src/spatext/observe.py
```

## 2026-07-11 - Terminal Seal After Narrow Findings

The tolerance-frontier and equal-emission findings above are
`ADDRESSED_PENDING_REVIEW`. The final replacement contract tuple is:

```text
cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d  spec/synth_medium_latent_response_observation_recovery_gate.md
```

The full command evidence and exact dispositions are recorded in the preceding
`Final Narrow Contract Correction Seal` entry. Post-correction status is:

```text
Task 1 independent review: ACCEPT, unchanged hash-specific evidence
scientific-identifiability document re-review: PENDING
executor-readiness document re-review: PENDING
provenance/freeze document re-review: PENDING
Task 2: STOPPED
```

Prior scientific and provenance accepts remain hash-specific and
non-transferable. The source receipt is unchanged, all no-exposure checks pass,
and no source, test, dependency, receipt, Task 2, payload, artifact, seed,
simulation, calibration, holdout, staging, commit, or push action occurred.
## 2026-07-11 - Append-Only Chain Break Reconciliation

record_type: `provenance_chain_reconciliation_v1`
record_status: `PENDING_INDEPENDENT_CHAIN_ACCEPTANCE`
record_start_line: `1759`
preappend_line_count: `1758`
preappend_sha256: `e1f1b0712cf6347538deaef2c59cfb90fc86e677b836c2aafac14ba0a9920717`
trusted_legacy_prefix: `1-993@02bc617dd7967853b0d8b4146f749ec37f4f1cc0ad5f906f534431775758882a`
first_nontrusted_line: `994`

### Chain Break

- historical seal `1-1376@67a191414c7635a52dbd5b9006ca5513c882cb3a0681121663f7f4d2e040619e`: `INVALID_AS_CURRENT_PREFIX_SEAL_HISTORICAL_ONLY`
- current diagnostic `1-1376@9b97981d3f44d367f653911d698ec78f9b0ecf1a59c62d5a20062c28897ed4c0`
- historical seal `1-1560@15b5d3798f3d731e117a1949a9ca1c50a7b7a4e38a763e00cae4d3eb6346ad67`: `INVALID_AS_CURRENT_PREFIX_SEAL_HISTORICAL_ONLY`
- current diagnostic `1-1560@d637e7a326c7900d50dec7b36cba6f2f93ea1a2b5d60888b3ed88a2d065314b4`
- observed inserted/reordered range `1083-1207@7c27f131df62fafc8b24fc89feed917871ce37fe4cfe1085f5945a1efec7ff3f`; older material begins at current line `1214`.
- No claim is made that this is the only mutation because no trusted post-993 byte copy is present in this file.

### Current Range Manifest

- post-prefix suffix `994-1758@4fd9d314cba75528cda199019c0f1cf143b0124f597c4a207019fa172914460d`
- terminal range `1688-1758@c23bc8d8cefac987feaf2ce762c66ce00eb5d5e530b3922875b3b50a00ddfd9b`
- complete pre-reconciliation snapshot `1-1758@e1f1b0712cf6347538deaef2c59cfb90fc86e677b836c2aafac14ba0a9920717`
- lines `994-1758`: `QUARANTINED_HISTORICAL_NARRATIVE_NON_AUTHORITATIVE_FOR_CHAIN_CONTINUITY`
- Seals and accepts inside the quarantined range remain historical only and do not transfer to a current gate.

### Current Hash-Specific State

- Goal `cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20`
- Plan `df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e`
- Runbook `78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed`
- authoritative spec `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`
- source receipt `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- Task 1 test/source `842908091c6a19f306db91cfef9f9c3d2f07eeb6062003c713fc0e4d5fc17309` / `cfefe7ee14f0d9221fa73d96691c7b1657adbefa2f87f756c82c7019be73b74f`
- scientific-identifiability, executor-readiness, provenance/freeze: `PENDING`
- Task 2: `STOPPED`
- no exposure: no Task 2 source/test/script, payload, artifact, seed, simulation, calibration, preholdout receipt, holdout receipt, staging, commit, or push
- Git anchor: `HEAD=main=origin/main=remote/main=53462d0365babf2c8070714a930f69b4071af276`; remote Goal 023 branch absent

### New Root Protocol

This entry declares the break; it does not validate the historical intermediate seals.
After append, compute full-file line count `N` and SHA-256 `H`.
Independent acceptance requires every value above, Goal/spec identity, source-boundary cleanliness, and no exposure to reproduce exactly.
Required disposition: `CHAIN_RECONCILIATION_ACCEPT root_lines=1-N root_sha256=H trusted_legacy=1-993@02bc617dd7967853b0d8b4146f749ec37f4f1cc0ad5f906f534431775758882a quarantined_legacy=994-1758@4fd9d314cba75528cda199019c0f1cf143b0124f597c4a207019fa172914460d`.
Append that acceptance as a child with `parent_line_count=N` and `parent_sha256=H`.
Every later entry must name the exact full-file parent line count and SHA-256; insertion, deletion, reordering, or backfill is forbidden.
Task 2 remains stopped until the new root and all current hash-specific document reviews independently return `ACCEPT` with no Critical or Important finding.
## 2026-07-11 - Independent Chain And Contract Acceptance

record_type: `provenance_chain_acceptance_v1`
parent_line_count: `1807`
parent_sha256: `0e07d664e3a1e2be58b7930cf3a23ffc123456bcbba9f7654cc8335fe15100ad`

```text
CHAIN_RECONCILIATION_ACCEPT root_lines=1-1807 root_sha256=0e07d664e3a1e2be58b7930cf3a23ffc123456bcbba9f7654cc8335fe15100ad trusted_legacy=1-993@02bc617dd7967853b0d8b4146f749ec37f4f1cc0ad5f906f534431775758882a quarantined_legacy=994-1758@4fd9d314cba75528cda199019c0f1cf143b0124f597c4a207019fa172914460d
```

Hash-specific gate decisions:

```text
Task 1 spec/API review: ACCEPT
Task 1 code/numerical review: ACCEPT
scientific-identifiability review: ACCEPT
executor-readiness review: ACCEPT
provenance/freeze review: ACCEPT
```

Accepted authority tuple:

```text
Goal     cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20
Plan     df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e
Runbook  78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed
spec     0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d
receipt  5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb
Task 1 tests 842908091c6a19f306db91cfef9f9c3d2f07eeb6062003c713fc0e4d5fc17309
Task 1 source cfefe7ee14f0d9221fa73d96691c7b1657adbefa2f87f756c82c7019be73b74f
```

No Task 2 source/test/script, payload, artifact, seed, simulation, calibration,
preholdout receipt, holdout receipt, staging, commit, or push existed at this
gate. Task 2 is now `UNLOCKED` under the accepted authority tuple. Every later
Log append must name the exact full-file parent line count and SHA-256; insertion,
deletion, reordering, or backfill is forbidden.

## 2026-07-11 - Task 2a1 Core Exact Likelihood TDD

record_type: `task_2a1_core_exact_likelihood_tdd_v1`
parent_line_count: `1844`
parent_sha256: `63ecd873fc9a34500a318c903b5923931c15ba1f7744bcff088ac9c85db09780`
authority_spec_sha256: `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`
status: `IMPLEMENTED_PENDING_INDEPENDENT_REVIEW`

### Strict RED Evidence

- Tests were written before the production module.
- RED test path: `tests/test_synth_medium_latent_response_observation_recovery.py`
- RED test SHA-256: `91b270ae88ec54533ae37cc33aa0a47ae0507092703b873141586dc5a1e0c59b`
- Exact command: `uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov`
- Exact result: exit `1`; `77` collected, `76` failed, `1` passed.
- Failing behavior IDs: `test_lro_2a1_001` through `test_lro_2a1_030`, including their parameterized cases.
- Failure: every failing case raised `ModuleNotFoundError: No module named 'spatext.synth.medium.latent_response_observation_recovery'` because production code did not yet exist.
- The sole passing case was the shared Poisson-helper boundary check `test_lro_2a1_031`.

### Implemented Core

- Test path: `tests/test_synth_medium_latent_response_observation_recovery.py`
- Source path: `src/spatext/synth/medium/latent_response_observation_recovery.py`
- Final test SHA-256: `19c8bb8bd7bf8ae7b677276822cbd0a6fe040c440c163a9c09948bb0c7dfed61`
- Final source SHA-256: `36ca1b8c7b311eb76fa1303cca8ea2a7d7eefc3dac96f23c22acc2a9fb9ab2ea`
- Frozen contracts: `ProcessParameters`, `JointParameters`, `CountOpportunity`, `AnalystHistory`, `ProcessOracleOutcome`, `ObservationOracleHistory`, and `LatentProcessTruth`; analyst, oracle, and evaluator objects are physically separate immutable types.
- Public exact-likelihood API: `process_log_primitives`, `hazard_probabilities`, `transition_log_path_masses`, `process_oracle_log_likelihood`, `observation_oracle_log_likelihood`, `joint_log_likelihood_enumeration`, `joint_log_likelihood_forward`, and `joint_path_posterior_weights`.
- Behavior IDs `test_lro_2a1_001`-`031` cover supports/order and schema validation; stable hazard primitives and TP removal at `beta_driver=0`; post-transition absorbing event/censor paths and normalized masses; process and observation oracle likelihoods; enumeration/independent-forward/brute-force equality over one, two, and 20 intervals; zero counts, no retained observations, irregular/coarsened opportunities, and intervening hazards; normalized 21-path posterior weights; analyst/truth firewall; explicit invalid/nonfinite objective failures; and the observation-kernel import boundary.

### GREEN And Static Evidence

- `uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov` -> exit `0`; `77 passed in 0.17s`.
- `uv run pytest tests/test_observe.py --no-cov` -> exit `0`; `48 passed in 0.14s`.
- `uv run ruff format --check tests/test_synth_medium_latent_response_observation_recovery.py src/spatext/synth/medium/latent_response_observation_recovery.py` -> exit `0`; `2 files already formatted`.
- `uv run ruff check tests/test_synth_medium_latent_response_observation_recovery.py src/spatext/synth/medium/latent_response_observation_recovery.py` -> exit `0`; `All checks passed!`.
- `uv run mypy src tests` -> exit `0`; `Success: no issues found in 59 source files`.
- `git diff --check` -> exit `0`; no output.

### Self-review And Boundary

- Source-only scope scan command: `rg -n 'numpy\\.random|np\\.random|SeedSequence|PCG64|scenario_id|split_id|replicate_index|Halton|L-BFGS|optimize|minimize|profile|artifact|holdout|bootstrap|schedule' src/spatext/synth/medium/latent_response_observation_recovery.py`; no matches.
- No RNG payload, random draw, simulation, schedule/scenario suite, design diagnostic, noncollision audit, transform, Halton start, optimizer, profile, CLI, artifact, calibration, holdout, receipt, staging, commit, or push was created or begun.
- Task 2a2 and Task 2b remain unstarted.
- Independent Task 2a1 review is `PENDING`; this entry makes no independent-review claim.

## 2026-07-11 - Task 2a1 Firewall And Immutable-array Review Fix

record_type: `task_2a1_review_fix_tdd_v1`
parent_line_count: `1889`
parent_sha256: `2934b563d1c28bf9dc9cda7267ba932d1cd06c39bbc133936b5077a82656486f`
authority_spec_sha256: `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`
independent_science_review: `ACCEPT`
code_firewall_rereview: `PENDING`
status: `REVIEW_FINDINGS_FIXED_PENDING_CODE_FIREWALL_REREVIEW`

### Independent Findings And Disposition

1. `IMPORTANT`: float and tuple subclasses could retain hidden metadata or overloaded arithmetic/iteration after validation and alter analyst-only likelihood evaluation. Disposition: fixed by exact built-in primitive checks, exact tuple checks, exact dataclass element checks, canonical validated copies, and canonical float storage via `object.__setattr__` in frozen contracts.
2. `IMPORTANT`: public arrays were owner-backed read-only NumPy arrays, so callers could run `setflags(write=True)`, mutate them, and invalidate path masses or later calculations. Disposition: fixed by copying every public float64 array into an immutable `bytes` buffer and exposing a NumPy view whose writability cannot be restored.

### Strict RED Evidence

- Tests were changed before production source.
- RED test path: `tests/test_synth_medium_latent_response_observation_recovery.py`
- RED test SHA-256: `5321062bfe52574ee34c39d028ff6b6e01f85dce696f7b66f99855204ba4a223`
- Exact command: `uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov`
- Exact result: exit `1`; `98` collected, `21` failed, `77` passed in `0.31s`.
- `test_lro_2a1_032`: five hostile-float cases failed with `DID NOT RAISE ValueError` for process parameters, joint rates, analyst quality, analyst arrival, and opportunity effort.
- `test_lro_2a1_033`: two revealing-tuple cases failed with `DID NOT RAISE ValueError` for analyst opportunities and observation-oracle states.
- `test_lro_2a1_034`: six hostile-integer cases failed with `DID NOT RAISE ValueError` for cell ID, time, count, state, transition time, and interval count.
- `test_lro_2a1_035`: all seven public-array cases failed with `DID NOT RAISE ValueError` when restoring writability on `driver`, `eta`, `log_survival`, `log_hazard`, hazards, path masses, and posterior weights.
- `test_lro_2a1_036`: canonical-storage assertion failed because exact built-in integer inputs remained stored as integers instead of canonical floats.

### Implementation And GREEN Evidence

- Exact built-in `int`/`float` inputs are accepted at numeric boundaries; `bool` and all numeric subclasses are rejected before conversion or arithmetic. Valid exact integers for float-valued fields are copied to built-in `float` storage.
- Analyst and oracle tuple containers must be exact built-in tuples. Opportunities are rebuilt as exact `CountOpportunity` values; states and primitive endpoints require exact integers; `ProcessLogPrimitives` requires exact float64 NumPy arrays and rebuilds them on immutable storage.
- Immutable public arrays use `np.frombuffer(canonical.tobytes(order="C"), dtype=np.float64)` and preserve the frozen float64 shapes and values.
- First GREEN attempt: the focused command exited `1` with `16 failed, 82 passed`; all failures were `NameError: _readonly_float_array is not defined` from one remaining private path-term return. Replacing that leftover call with `_immutable_float_array` resolved it.
- A first `uv run mypy src tests` static attempt exited `1` with `10` narrowing errors because mypy did not infer an `object` as numeric from exact `type` checks. Explicit post-check `cast(int | float, value)` narrowing resolved these without changing runtime acceptance.
- Final `uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov` -> exit `0`; `98 passed in 0.17s`.
- Final `uv run pytest tests/test_observe.py --no-cov` -> exit `0`; `48 passed in 0.13s`.
- `uv run ruff format --check tests/test_synth_medium_latent_response_observation_recovery.py src/spatext/synth/medium/latent_response_observation_recovery.py` -> exit `0`; `2 files already formatted`.
- `uv run ruff check tests/test_synth_medium_latent_response_observation_recovery.py src/spatext/synth/medium/latent_response_observation_recovery.py` -> exit `0`; `All checks passed!`.
- `uv run mypy src tests` -> exit `0`; `Success: no issues found in 59 source files`.
- `git diff --check` -> exit `0`; no output.

### Final Hashes And Boundary

- Final test SHA-256: `5321062bfe52574ee34c39d028ff6b6e01f85dce696f7b66f99855204ba4a223`
- Final source SHA-256: `78169d0114029287fd9a81bd5024b632a4060a8b27b8a14839d616a85d35bdb1`
- No RNG, Task 2a2/2b, scenario, simulation, artifact, calibration, holdout, staging, commit, or push work was created or begun.

## 2026-07-11 - Task 2a1 Independent Firewall Re-review Acceptance

record_type: `task_2a1_independent_firewall_rereview_v1`
parent_line_count: `1937`
parent_sha256: `8f9933e4a96843c2ac9b711c9cdb25082aa7b088111bd3370baeb160c043a9a6`
authority_spec_sha256: `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`
reviewer_agent_id: `019f4fc3-ca03-7822-b7c9-8649068ac69a`
verdict: `ACCEPT`
status: `TASK_2A1_ACCEPTED`

### Reviewed State

- Source SHA-256: `78169d0114029287fd9a81bd5024b632a4060a8b27b8a14839d616a85d35bdb1`.
- Test SHA-256: `5321062bfe52574ee34c39d028ff6b6e01f85dce696f7b66f99855204ba4a223`.
- The reviewer re-read the current files and returned exactly `ACCEPT` after checking the repaired hostile numeric/container-subclass boundary, immutable public-array storage, analyst/truth firewall, and likelihood semantics.

### Orchestrator Verification

- `uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov` -> `98 passed`.
- `uv run pytest tests/test_observe.py --no-cov` -> `48 passed`.
- Targeted Ruff format and lint checks passed.
- `uv run mypy src tests` -> no issues in `59` source files.
- `git diff --check` passed.
- No Task 2a2/2b, scenario, calibration, holdout, artifact, staging, commit, or push work preceded this acceptance.

## 2026-07-11 - Task 2a2 Deterministic Simulation And Design Primitives TDD

record_type: `task_2a2_simulation_schedule_diagnostics_tdd_v1`
parent_line_count: `1962`
parent_sha256: `b047ab616b7292661b311c3ad227543df3556ad2dbcd9c9117257a60f92f4aad`
authority_spec_sha256: `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`
status: `IMPLEMENTED_PENDING_INDEPENDENT_REVIEW`

### Strict RED Evidence

- The Task 2a2 tests were added before any production-source change. At RED,
  the accepted Task 2a1 source still had SHA-256
  `78169d0114029287fd9a81bd5024b632a4060a8b27b8a14839d616a85d35bdb1`.
- RED test SHA-256:
  `159e9baabf34f9bead1458514094e00242b5544c14bc8c995d11122441aa76c6`.
- Exact command:
  `uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov`.
- Exact RED result: exit `1`; `123` collected; `21 failed, 99 passed, 3 errors in 0.67s`.
  Every failure/error was the expected missing Task 2a2 API (`DesignCell`,
  canonical RNG helpers, simulation, schedules/frames, or diagnostics); all
  accepted Task 2a1 behavior remained green.
- Self-review found the timing-only equal-emission exception needed base
  `process` and `observation` development indices through `23`. A second test-first
  run exited `1` with `1 failed, 122 passed in 1.03s`; the validator then received
  the minimum component-specific exception while predictive/PIT indices remained
  capped at `11`.

### Implemented Task 2a2 Surface

- Exact schema validation precedes RNG construction; compact sorted-key ASCII
  JSON, SHA-256, eight big-endian entropy words, `SeedSequence`, and
  `Generator(PCG64DXSM(...))` reproduce both frozen development/calibration
  raw-`uint64` vectors.
- Process simulation consumes one complete C-order float64
  `(n_passable, 20)` uniform array before applying absorbing recursion. Count
  simulation makes one Poisson call over the full canonical mean vector and
  returns truth-free immutable `AnalystHistory` values.
- Literal process/dense/structured/sparse schedules, structured effort, the
  1306-cell sparse frame, exact quality quintiles, within-block arrival
  permutation, and the 1045/4180 alignment frame are deterministic and ordered
  by integer cell ID then time.
- `potential_design`, `process_oracle_truth_at_risk`, and
  `joint_plugin_smoothed_at_risk` carry separate provenance/role labels. The
  generalized float64 SVD rank/condition convention is shared; plug-in at-risk
  weights use normalized analyst-only path masses. Oracle truth has no joint
  likelihood or plug-in interface.
- Public simulation/weight/permutation arrays are exact-shape, exact-dtype,
  C-contiguous immutable byte-buffer views. Invalid schemas, domains, order,
  component/split/index combinations, and RNG-return shapes fail explicitly.

### GREEN, Regression, And Static Evidence

- Final focused command -> exit `0`; `123 passed in 0.63s`.
- Observation-kernel regression -> exit `0`; `48 passed in 0.14s`.
- Upstream regressions without coverage: landscape `5 passed`, spread impact
  `5 passed`, observation design `5 passed`, and recoverability-target
  observation design `6 passed`.
- Targeted Ruff format -> `2 files already formatted`; targeted Ruff lint ->
  `All checks passed!`.
- `uv run mypy src tests` -> `Success: no issues found in 59 source files`.
- `git diff --check` -> exit `0`; no output.
- Source-scope scan for `scipy.optimize|minimize|brentq|qmc.Halton`, artifact
  paths, and a holdout receipt returned no matches.

### Final Hashes, Self-review, And Boundary

- Test SHA-256:
  `921775bf7c9516d7df0749e6e61a1c315c0b1aa7e80a9c05a364f26dc31bc286`.
- Source SHA-256:
  `b61a3f7186a20748dc853f9f7fce8e3a04d008594ad2b64ce0139cebe1980486`.
- Frozen spec remained
  `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`.
- Self-review confirmed the analyst/truth split, exact stochastic consumption,
  zero-based non-holdout partition boundaries, deterministic canonical order,
  and absence of optimizer/profile/noncollision/scenario-suite/CLI/artifact
  work.
- Holdout payload construction remains hard-locked; no holdout payload was
  instantiated or inspected. No artifact, calibration run, receipt, staging,
  commit, push, or generated deliverable was created.

## 2026-07-11 - Task 2a2 Independent Review Acceptance

record_type: `task_2a2_independent_review_acceptance_v1`
parent_line_count: `2042`
parent_sha256: `4f1773f513e35378a5126772d37c3f86c0cf69ea8560b81ebe4720ed622461e8`
authority_spec_sha256: `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`
status: `TASK_2A2_ACCEPTED`

### Bound State

- Source SHA-256: `b61a3f7186a20748dc853f9f7fce8e3a04d008594ad2b64ce0139cebe1980486`.
- Test SHA-256: `921775bf7c9516d7df0749e6e61a1c315c0b1aa7e80a9c05a364f26dc31bc286`.
- RNG/determinism/code reviewer `019f4ff5-9ce9-78a2-a3f5-0b57ba4ae457`: `ACCEPT`; no Critical, Important, or Minor finding.
- Science/likelihood/firewall reviewer `019f4ff5-9d7f-7711-b401-0590df5b63b4`: `ACCEPT`; no Critical, Important, or Minor finding.
- Provenance/boundary reviewer `019f4ff5-9e16-7b02-86a7-c969eb1fb3b8`: `ACCEPT`; no Critical, Important, or Minor finding.

### Acceptance Basis

- Exact seven-key payload validation and rejection before RNG construction, both frozen non-holdout vectors, full process and observation draw consumption, canonical ordering, immutable public arrays, and literal schedule/frame definitions were independently verified.
- Endpoint timing, absorbing transitions, emission semantics, analyst-only histories, plug-in at-risk weights, and the separation of potential, oracle, and practical design diagnostics were independently accepted.
- The append-only chain, Task 2a2 write scope, accepted authority tuple, clean base, absence of optimizer/profile/scenario-runner/artifact/calibration/receipt work, and the hard pre-RNG holdout lock were independently accepted.
- Orchestrator verification passed: `123` focused tests, `48` observation-kernel regressions, `21` upstream synth-medium regressions, targeted Ruff format/lint, `mypy src tests`, and `git diff --check`.

Task 2a is accepted. Task 2b may begin. Holdout remains uninstantiated and locked.

## 2026-07-11 - Binding Holdout-Provenance Interpretation

record_type: `holdout_provenance_binding_interpretation_v1`
parent_line_count: `2067`
parent_sha256: `76516a50cdb78d83d3d86267afa527671cc599c00b459009cd383dcc1a091a1a`
authority_spec_sha256: `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`
status: `BINDING_PENDING_INDEPENDENT_ACCEPTANCE_AND_TESTS`

This entry resolves only provenance and temporal interpretation. It changes no
estimand, equation, parameter support, scenario, schedule, replicate count,
gate, denominator, recommendation precedence, RNG mapping, schema field, or
scientific conclusion. Holdout exposure remains prohibited until the required
tests and independent reviews accept this exact interpretation.

### Immutable Receipt Fields

`holdout_receipt.json` is an immutable exposure receipt, not a mutable terminal
disposition record.

- `exposed = true` means exclusive atomic receipt creation irrevocably committed
  and burned the named holdout namespace; it does not assert that every
  scientific row was subsequently emitted.
- `invalidated = false` means no invalidating event was known at the instant of
  atomic receipt creation.
- `no_contract_change = true` means the analytical tracked-state digest matched
  the frozen preholdout receipt and config at that instant.
- `receipt_sha256` authenticates those exposure-time assertions with that field
  omitted from its own canonical hash payload.
- The same fields in `holdout_manifest.json` reproduce that receipt-time
  snapshot and are not a later mutable disposition channel.

A crash, partial failure, mutating check, or later review finding never rewrites
either object. It burns the namespace and is recorded in the append-only
provenance plane. A finding requiring an analytical tracked change sets the
publication disposition to `STOP_INVALIDATED_POST_EXPOSURE`; it does not alter
the receipt's historical exposure-time assertions.

### Literal Analytical Tracked Manifest

"Every allowed tracked path" means the exact Runbook section 8 publication
allowlist. The analytical digest membership is that allowlist minus only
`Log.md`, `preholdout_state_receipt.json`, and `holdout_receipt.json`.
The literal lexically sorted 16-path manifest is:

```text
AGENTS.md
README.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
pyproject.toml
scripts/run_synth_medium_latent_response_observation_recovery.py
spec/report_log.md
spec/synth_medium_latent_response_observation_recovery_gate.md
src/spatext/observe.py
src/spatext/synth/medium/__init__.py
src/spatext/synth/medium/latent_response_observation_recovery.py
tests/test_observe.py
tests/test_synth_medium_latent_response_observation_recovery.py
uv.lock
```

No glob, import walk, live `git ls-files` result, dirty-path set, or runtime
discovery may add or omit a member. Every member must exist as a regular file at
freeze. The aggregate is SHA-256 over lexically sorted UTF-8 lines of
`<file_sha256><two spaces><relative_path>\n`. The preholdout receipt manifest
must equal this exact path set and order. Final publication still requires all
19 allowlisted tracked paths, including the three digest exclusions.

### Config And Digest Ordering

The ignored config is emitted only after all 16 analytical files exist and all
permitted analytical edits are complete. The implementation must:

1. Compute the exact 16-file manifest and `tracked_state_sha256` from disk.
2. Emit the candidate config containing that digest.
3. Compute `config_sha256` from canonical config bytes with only
   `config_sha256` omitted; `tracked_state_sha256` remains in the hash payload.
4. Independently review the exact config bytes, config hash, manifest, tracked
   digest, source hash, and spec hash together.
5. Rerun the complete preholdout ladder; any analytical mutation returns to
   step 1 and requires a newly emitted and reviewed config.
6. Make `freeze-tracked-state` reproduce, never patch or regenerate, the
   config's digest before atomically creating the preholdout receipt.

Thus Task 4's later `compute` step is an independent freeze-time reproduction of
an already embedded and reviewed digest.

### Post-Holdout Provenance Write Scope

After atomic receipt creation, the only permitted tracked writes are the
machine-created immutable `holdout_receipt.json` and append-only,
provenance-only records at the end of this `Log.md`. The Plan's machine-created
receipt limit applies to scientific-command output and analytical tracked state;
it does not revoke the separately defined append-only provenance plane.

Every post-exposure Log append must reproduce its exact parent, bind the
authority/config/tracked-state/receipt/artifact hashes, identify reviewer role
and immutable disposition, change no analytical contract or artifact result,
and use only `CONTINUE_FROZEN_CANDIDATE` or
`STOP_INVALIDATED_POST_EXPOSURE` as applicable. Reviewers are read-only; one
designated provenance writer performs exact appends.

### Potentially Mutating Validation

Before freeze, `pre-commit run --all-files` and every potentially mutating
validation command must be proven a no-op on the exact candidate. Post-exposure,
capture the 16-file manifest, aggregate digest, and status immediately before
and after each such command. Accept it only if it exits zero and changes no
tracked byte. Any mutation is an invalidating event, not an authorized repair:
preserve state and receipts, record `STOP_INVALIDATED_POST_EXPOSURE`, and stop
without restore, rerun, amendment, or namespace reuse.

### Task 6 Validation Ladder

Task 6 `full validation ladder` means Runbook section 7 post-holdout read-only
verification, artifact/receipt/digest/status guards, exact 19-path staging,
`git diff --cached --check`, `verify-staged-state`, fresh final review, exact
terminal-attestation append verification, and repetition of nonmutating guards
immediately before commit. It does not mean Runbook section 4. After exposure,
never delete the bundle, rerun calibration/runtime benchmarking/holdout, or
regenerate a scientific artifact.

### Final Review Without Recursion

All ordinary post-holdout review records must be appended and staged before the
fresh final review. That reviewer inspects the exact cached candidate, immutable
config/artifacts/receipts/evidence, live 16-file digest, exact 19-path staged
set, and an exact proposed terminal-attestation payload including its live Log
parent count and hash.

On acceptance, the returned terminal-attestation payload is itself the approved
append. The provenance writer appends those exact bytes once, stages `Log.md`,
and proves unchanged prefix, byte-identical approved suffix, reproduced parent,
unchanged analytical digest/receipts/config/artifacts/non-Log staged blobs, and
that no further Log append will occur before commit. No second statement about
that append is permitted. Rejection appends no acceptance record; a required
analytical change invalidates the exposed namespace.

### Required Executable Gate

Before freeze, tests must cover receipt exposure-time values/self-hash, receipt
creation before RNG and burned-namespace failure, immutable receipt after later
invalidation, exact 16-path manifest and malformed variants, config/digest
ordering, failed freeze without mutation, atomic preholdout receipt creation,
append-only Log parent verification, no-op hook qualification and mutation
invalidation, Task 6's post-holdout-only dispatch, and exact one-time terminal
attestation. These tests must use temporary non-holdout fixtures and may not
instantiate, derive, preview, or inspect a Goal 023 holdout payload.

Until those tests pass and hash-specific scientific, executor-readiness, and
provenance/freeze reviewers accept this entry with no Critical or Important
finding, status remains `HOLDOUT_BLOCKED_PENDING_BINDING_ACCEPTANCE_AND_TESTS`.

## 2026-07-11 - Task 2b Interrupted-worker Verified Checkpoint

record_type: `task_2b_verified_checkpoint_v1`
parent_line_count: `2222`
parent_sha256: `a531eb33d0afb1ffdb91efcf0cddc37bd0b8327269b074bb175b566a85039203`
authority_spec_sha256: `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`
status: `IMPLEMENTED_GREEN_PENDING_INDEPENDENT_REVIEW_AND_CONTRACT_AMENDMENT`

Two Task 2b workers were stopped after prolonged nonresponsive reasoning, while
their shared-worktree edits were preserved. This record makes no unsupported
RED-sequence claim. It binds only the independently reproduced current state.

- Source SHA-256: `d732977d6bb6ae966d4e8575e4ad242d0054d826414ba00846d2e1e0b827bfa3`.
- Test SHA-256: `3d92ab723aed2a14b27aaebb6080917999ed9a0bf7a2de60aed65e90222b2ef9`.
- Focused command: `uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov`.
- Result: `194 passed in 737.23s`.
- Targeted Ruff format and lint passed; `uv run mypy src tests` reported no
  issues in `59` source files; `git diff --check` passed.
- The implementation covers the ordered-rate maps, deterministic Halton starts,
  separate batched likelihood/posterior kernels, literal optimizer adapter,
  generalized diagnostics, nine canonical inverse audits and failure fixtures,
  adaptive profiles, and fit preflight/firewall surfaces asserted by the 194
  tests.
- No scenario replication, calibration, artifact, CLI, receipt, staging,
  commit, push, or holdout payload was created or run.

Task 2b is not accepted until independent numerical, identifiability,
firewall/provenance, and code reviews pass. The prior Log-only provenance
interpretation is rejected by executor/provenance review and must be replaced
by the prepared tracked contract amendment before Task 3 or any freeze/holdout
work. Holdout remains locked and uninstantiated.

## 2026-07-11 - Task 2b Max-Audit Repair Checkpoint

record_type: `task_2b_max_audit_repair_v1`
parent_line_count: `2254`
parent_sha256: `a59540d9bcbca47b8277499a596d16d8e3e7be2f592ce1ab848c0070f4d19094`
authority_spec_sha256: `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`
repair_brief_sha256: `0f3746da086237bc2e423e012f3493caf3bbb1671758d2263ba151deac8507bf`
max_audit_sha256: `e9117f1286ef378f95bed056afd3dd4c11487d79c6b2637196e3c38974bd5309`
status: `REPAIRED_GREEN_PENDING_INDEPENDENT_REREVIEW`
independent_rereview_status: `PENDING`

The two Important max-audit findings were repaired under the exact fix brief.
Every deployable process-oracle, observation-oracle, and joint fit/profile route
now requires a factory-issued typed nine-audit preflight; each route constructs
its objective internally from its exact typed data; joint routes remain
analyst-only and batched; and raw callback optimizer/profile engines are private.
Directly constructed or incomplete preflight records cannot authorize work.
All finite canonical predator arrivals are retained without a horizon recode.

- Firewall RED: with source still at
  `d732977d6bb6ae966d4e8575e4ad242d0054d826414ba00846d2e1e0b827bfa3`,
  the three focused factory/typed-route/fabrication tests failed `3/3` in
  `0.48s`; the identical command then passed `3/3` in `0.32s`.
- Arrival RED: the two source-bound tests errored `2/2` in `0.80s` at the first
  preserved source value above the old cap, `120.576984839346`; after removing
  only the upper-horizon rejection, the identical command passed `2/2` in
  `0.61s`.
- Broad fast latent-recovery regression: `194 passed, 5 deselected in 2.45s`.
- Observation and relevant upstream synth-medium regression set: `79` tests,
  exit `0`, approximately `26.3s`.
- Final full latent-recovery file: `199 passed in 772.21s` (`real 772.46s`).
  The nine recovery counts remained dense `16/15/2`, structured `16/14/3`,
  sparse `15/16/16`, with zero collisions.
- Direct raw-versus-old-recode comparison over all three schedules and all
  three targets had maximum absolute audit-vector and scaled-Jacobian
  differences exactly `0.0`. Canonical arrivals were `5225/5225` finite,
  `620` above `120`, maximum `205.910318172679`; the permutation/correlation
  frame retained `5225` finite pairs.
- Targeted Ruff format/lint passed; `uv run mypy src tests` passed for `59`
  source files; `git diff --check` passed.

Final implementation hashes before this append:

- source SHA-256: `701dd468219737d8885a2f52ef9e4cbb8965397277f6b9d1a4f3ebbfe72bc673`;
- tests SHA-256: `cb18204c6c78e9a0a1f049198f563b131cd3ee8d84793d1dfa94a87d6f68b6aa`.

Repair report: `.superpowers/sdd/task-2b-audit-fix-report.md`. No Task 3 work,
scenario/calibration run, holdout payload, artifact, receipt, authority edit,
staging, commit, or push was performed. Task 2b remains unaccepted until an
independent rereview reports no Critical or Important finding.

## 2026-07-11 - Task 2b Independent Acceptance Child

record_type: `task_2b_independent_acceptance_v1`
parent_line_count: `2305`
parent_byte_count: `113393`
parent_sha256: `7a95d0ce27fb7ffa9e9ec77308659a68b243f79f986b85ecdb518d7365ebd5b6`
source_sha256: `701dd468219737d8885a2f52ef9e4cbb8965397277f6b9d1a4f3ebbfe72bc673`
test_sha256: `cb18204c6c78e9a0a1f049198f563b131cd3ee8d84793d1dfa94a87d6f68b6aa`
rereview_sha256: `aa4da61aec534282ff8302b989a46bb1298cc0c8596b4b9af9efe42e08548306`
status: `ACCEPTED_TASK_2B_PENDING_INTEGRATED_AMENDMENT`

The independent Task 2b repair rereview reports `SUPPORTED` with no Critical or
Important finding. This child accepts the exact source and test handoff for the
bounded integrated pre-Task-3 amendment only. It authorizes the required
append-only amendment records and non-holdout RED/GREEN implementation; it
does not authorize Task 3 scenarios, runtime benchmarking, calibration,
artifacts, config, receipts, holdout, staging, commit, push, or publication.

## 2026-07-11 - Holdout-Provenance Interpretation Supersession

record_type: `holdout_provenance_binding_interpretation_v1_disposition`
parent_line_count: `2323`
parent_byte_count: `114393`
parent_sha256: `47b6d6a9bd971353f9e090f200ae805f310582834ad8c2f1f1b9d9d698823891`
target_record_type: `holdout_provenance_binding_interpretation_v1`
target_record_start_line: `2069`
target_record_end_line: `2222`
status: `superseded_pending_amendment`

The target interpretation remains preserved byte for byte but is not authority
for holdout exposure. Independent review found unresolved provenance execution
gaps: explicit post-exposure Log authorization in tracked authority, complete
immutable-byte guards around every post-exposure command, pinned identity and
candidate-footprint guards at config emission/freeze/pre-receipt/pre-RNG, and
a terminal disposition plus controlled one-retry rule for unchanged nonzero
validation. This disposition changes no science and authorizes no holdout
construction or exposure. Holdout remains blocked pending the integrated
tracked amendment, executable non-holdout tests, hash resealing, and fresh
hash-specific acceptance.

## 2026-07-11 - Integrated Pre-Task-3 Contract Amendment

record_type: `integrated_pre_task3_contract_amendment_v1`
parent_line_count: `2345`
parent_byte_count: `115553`
parent_sha256: `243095ced7e490757e571277c41c51b46aff4fc76e3f9d5190dc68dc73be0e68`
goal_sha256: `1c95ca0bb3327767f3c33bd92e0644bacc5f9037b64d2c2b5271ec0dd4ecae60`
plan_sha256: `23cbf3bb430b9ca442e4417f51287daa85565e44ea1c51d49ecc4281c2427b55`
runbook_sha256: `3b3fc38c8aadc0b9bd802bd93b2456d26f15a5ec4711ee304ea0de4043644f66`
authority_spec_sha256: `803c5e370c23f8144c36c48b07ab15dffacb7ff55e7267ea68303d890e726572`
source_sha256: `be97ca6524eb312bff5e82a26412c58978fb8435fc1ed19ee7868b1ce22e0ae5`
test_sha256: `f080ea83124ce7fa57f6d8dbcbdb5eaca923075378a4f3eb0410340ba4ec6f64`
source_receipt_sha256: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
proposal_sha256: `ee367b6014bf823ffda2f406186179271a0f0e56ac955ea35ae6fb11c3bea15d`
pinned_branch: `codex/spatext-goal023-latent-response-observation-gate`
pinned_head: `53462d0365babf2c8070714a930f69b4071af276`
pinned_base: `53462d0365babf2c8070714a930f69b4071af276`
status: `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`
review_scientific: `PENDING`
review_statistical: `PENDING`
review_executor_readiness: `PENDING`
review_artifact_schema: `PENDING`
review_code: `PENDING`
review_provenance_freeze: `PENDING`

The accepted Task 2b handoff and the provenance-interpretation supersession
child are parent-bound immediately before this record. RED behavior-specific
tests were added for the literal registry and fit identity, latent ordered
21-path diagnostics, fail-closed four-class reduction, exact 22-file two-level
hash interfaces, typed config identity, and fixture-only calibration dispatch.
The RED command selected 11 tests and failed `11/11` on absent amendment
surfaces; the focused GREEN command selected 12 compatibility/amendment tests
and passed `12/12`. The complete latent-recovery file passed `210` tests in
`771.37s`; the observation and upstream synth-medium regression set passed
`79` tests in `80.28s`. Ruff format/check, mypy, and `git diff --check` passed.

No Task 3 scenario, runtime benchmark, calibration, artifact, config, receipt,
holdout payload, staging, commit, push, or publication was run or created.
Fresh independent scientific, statistical, executor-readiness, artifact/schema,
code, and provenance/freeze review remains required before Task 3 is ready.

## 2026-07-11 - Integrated Amendment Max-Audit Repair

record_type: `integrated_amendment_max_audit_repair_v1`
parent_line_count: `2386`
parent_byte_count: `117981`
parent_sha256: `7d1900eeff1af5cc04455dc7cf792d882fe9c128277713d51b3116a563c5e55b`
status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
binding_status: `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`
branch: `codex/spatext-goal023-latent-response-observation-gate`
head: `53462d0365babf2c8070714a930f69b4071af276`
base_ref: `origin/main`
base_commit: `53462d0365babf2c8070714a930f69b4071af276`

This child repairs the one Critical and four Important findings in the
independent integrated-amendment max audit. Every parent byte is preserved as
the exact prefix. The accepted Task 1/2 scientific kernel, model equations,
estimands, supports, generating values, schedules, numerical gates, seed
contract, and source receipt are unchanged. The repair applies the complete
tracked authority, adds the exact 98 named pre-Task-3 behaviors, and implements
the missing registry, typed evidence, denominator, latent-row, reducer,
artifact/hash, phase, envelope, retry, staging, and publication guards.

Bound hashes:

- Goal: `6883c0188be06c328f09a4e07a9872b366e414abac31bc5241b7d5c72f6b8e3f`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `fc74fae83c6e93701a06d342346ffe803360fb718f2ed34f69bcb610103a7e7b`
- authoritative spec: `af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e`
- source: `a862b269f85ae67b479e8df463582ea4019ce46abae7f20b0cacd6fa75d25458`
- tests: `e0b0ba396e48c02d51f4477260fd96790e167d8dadb94bce9e674faa2e490ae0`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`

Grouped RED evidence, observed before each implementation group:

- `T3A-001..011`: exact command selected `lro_3a`; `11 failed`, exit `1`,
  on absent literal registry/firewall/fit-identity behaviors.
- `T3L-001..020`: exact command selected `lro_3l`; `14 failed, 6 passed`,
  exit `1`, on the missing row/applicability layer while accepted kernel tests
  remained green.
- `T3D-001..014`: exact command selected `lro_3d`; `14 failed`, exit `1`,
  on absent denominator/control/stress reducers.
- `T3R-001..020`: exact command selected `lro_3r`; `20 failed`, exit `1`,
  on absent local reducers and canonical total state machine.
- `T3S-001..010`: exact command selected `lro_3s`; `9 failed, 1 passed`,
  exit `1`, on incomplete artifact/hash/fixture interfaces.
- `T3P-001..023`: exact provenance selector returned `22 failed`; the omitted
  never-retry name was included in the complete group GREEN selector.

GREEN and validation evidence:

- complete exact amendment matrix: `98 passed, 199 deselected in 0.26s`;
- complete Goal 023 source test file: `297 passed in 731.04s`;
- observation/upstream regressions: `69 passed in 46.95s`;
- `uv run ruff format --check .`: `PASS` on final bytes;
- `uv run ruff check .`: `PASS`;
- `uv run mypy src tests`: `Success: no issues found in 59 source files`;
- Goal/spec body equivalence: `PASS`;
- exact proposal-name inventory: `required=98 missing=0`;
- `git diff --check`: `PASS`;
- canonical artifact directory, preholdout receipt, and holdout receipt:
  `ABSENT`.

Review dispositions for this replacement tuple:

- scientific: `PENDING`
- statistical: `PENDING`
- executor-readiness: `PENDING`
- artifact/schema: `PENDING`
- code: `PENDING`
- provenance/freeze: `PENDING`
- independent max rereview: `PENDING`

No Task 3 scientific scenario, live benchmark, calibration, canonical artifact
or config, provenance receipt, holdout payload, staging, commit, or push was
run or created. Task 3 remains blocked until fresh hash-specific acceptance
and a clean independent max rereview of this replacement tuple.

## 2026-07-12 - Integrated Amendment Final-Rereview Complete Repair

record_type: `integrated_amendment_final_rereview_repair_v1`
parent_line_count: `2463`
parent_byte_count: `121774`
parent_sha256: `a074ede50e6fd797537efdc245bd85be23ebe01e00b74d666aa54ad665840a8e`
status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
binding_status: `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`
task_3_authority: `BLOCKED`
calibration_authority: `BLOCKED`
config_emission_authority: `BLOCKED`
freeze_authority: `BLOCKED`
holdout_authority: `BLOCKED`
branch: `codex/spatext-goal023-latent-response-observation-gate`
head: `53462d0365babf2c8070714a930f69b4071af276`
base_ref: `origin/main`
base_commit: `53462d0365babf2c8070714a930f69b4071af276`

This child repairs every Critical and Important finding in the 2026-07-12
integrated-amendment final rereview. Every parent byte is preserved as the
exact prefix. Goal, Plan, Runbook, authoritative spec, source receipt, Task 1/2
numerical science, model equations, estimands, supports, schedules, thresholds,
seed contract, and publication authority are unchanged.

Bound hashes:

- Goal: `6883c0188be06c328f09a4e07a9872b366e414abac31bc5241b7d5c72f6b8e3f`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `fc74fae83c6e93701a06d342346ffe803360fb718f2ed34f69bcb610103a7e7b`
- authoritative spec: `af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e`
- source: `421f0a9b9082c3c66002ce446a2444510b10a0205645e716de048ccda54bc116`
- tests: `dede165ea37c7fc2fb8709b00c72c45001bba2e7a42d5419b4d36696e2774f05`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`

Behavior-specific RED evidence was captured before implementation with the
exact affected-name selector. It selected 15 rereview counterexample tests and
returned `15 failed, 282 deselected`, exit `1`. The failures reproduced
registry/scope contradiction, incomplete successful-fit fields, duplicate
arrival variants, absent observed equal-emission reconstruction, short latent
frames, malformed latent row states, invalid control denominators, impossible
scenario-local reasons, extra represented artifacts, incomplete config and
receipt schemas, forged typed identities, hidden fixture RNG side effects,
`--phase=calibration`, replacing receipt creation, malformed post-receipt RNG
entry, and caller-approved out-of-allowlist staging.

The complete repair now uses injected Git command output plus real temporary
disk capture, parsed porcelain status and phase arguments, live revalidation,
exclusive non-overwriting receipts, complete canonical config/preholdout/
holdout schemas and cross-bindings, and zero RNG construction on every tested
mismatch. Fit rows reconcile to the literal registry, parameter subsets, all
six fit-derived key forms, duplicate-free fixed arrival frames, observed and
199 bootstrap equal-emission pairs, frozen denominators, and scenario-specific
canonical reason domains. Latent diagnostics require exact analyst/evaluator/
authority ID frames and complete typed row states while remaining
recommendation-neutral. Artifact representation, canonical typed identities,
observed fixture side effects, literal staging blobs, command parsing, retry,
publication transition, live supersession target, and terminal-envelope guards
now fail closed.

GREEN and validation evidence on the bound source/test tuple:

- exact proposal inventory: `98` unique names, `98 passed in 0.63s`;
- complete Goal 023 test file: `297 passed in 700.66s`;
- observation and upstream synth-medium regressions: `69 passed in 46.39s`;
- Ruff format check: `PASS`;
- Ruff check: `PASS`;
- mypy: `Success: no issues found in 59 source files`;
- `git diff --check`: `PASS`;
- Goal/spec body equivalence: `106597` bytes, SHA-256
  `855a3c3291dedf473fc1879601987f6126924e71123e4aa515b86805a3bb93eb`;
- existing parent-bound Log records verified: `13/13`;
- canonical artifact directory, recovery config, preholdout receipt, and
  holdout receipt: `ABSENT`;
- Git index: `EMPTY`.

Review dispositions for this replacement tuple:

- scientific: `PENDING`
- statistical: `PENDING`
- executor-readiness: `PENDING`
- artifact/schema: `PENDING`
- code: `PENDING`
- provenance/freeze: `PENDING`
- independent max rereview: `PENDING`

No Task 3 scenario, RNG construction, live runtime benchmark, calibration,
canonical output write, scientific row, artifact, config, receipt, holdout
payload, holdout exposure, staging, commit, push, publication, deletion, reset,
restore, or broad cleanup occurred. This is not acceptance. Task 3 and every
later irreversible phase remain blocked pending fresh hash-specific independent
review with no Critical or Important finding.

## 2026-07-12 - Integrated Amendment Final Rereview 2 Complete Repair

record_type: `integrated_amendment_final_rereview_2_repair_v1`
parent_line_count: `2555`
parent_byte_count: `126506`
parent_sha256: `9d6d8b0265720e7eef6102bdc6e8271517b030bdd1c29018c995d7b7d6d8e768`
status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
acceptance_status: `PENDING`
binding_status: `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`
task_3_authority: `BLOCKED`
calibration_authority: `BLOCKED`
config_emission_authority: `BLOCKED`
freeze_authority: `BLOCKED`
holdout_authority: `BLOCKED`
branch: `codex/spatext-goal023-latent-response-observation-gate`
head: `53462d0365babf2c8070714a930f69b4071af276`
base_ref: `origin/main`
base_commit: `53462d0365babf2c8070714a930f69b4071af276`

This child repairs every Critical and Important finding in
`integrated-amendment-final-rereview-2.md`. Every parent byte is preserved as
the exact prefix. Goal, Plan, Runbook, authoritative spec, observation kernel,
dependencies, lockfile, source receipt, Task 1/2 numerical science, estimands,
supports, schedules, thresholds, seed contract, and publication authority are
unchanged.

Bound hashes before this append:

- Goal: `6883c0188be06c328f09a4e07a9872b366e414abac31bc5241b7d5c72f6b8e3f`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `fc74fae83c6e93701a06d342346ffe803360fb718f2ed34f69bcb610103a7e7b`
- authoritative spec: `af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e`
- source: `fe2628800bd0db521a8649285ab0679ce81655877f1b0154c1e5d1b9dd69b180`
- tests: `d3f6cc1920f20c994e8f65ecefca637a5d3e13f46f0b8a0a905030c3231e3069`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- amendment proposal: `ee367b6014bf823ffda2f406186179271a0f0e56ac955ea35ae6fb11c3bea15d`
- final rereview 2: `1c9a374b18e33bc95bc7424aced6595197e356d3ab30aa32cd5d840a7f4e0906`

Behavior-specific RED evidence was captured before implementation with the
exact affected counterexample selector: `18 failed, 279 deselected in 1.05s`,
exit `1`. The failures independently reproduced nonnested calibration fits,
incomplete arrival frames, mixed equal-emission sources, absent zero-driver
fit/profile evidence, malformed failed-fit and predictive states,
contradictory reducer evidence, forged latent frames, incomplete config
literals, hidden fixture side effects, unbound retry commands, create-before-
validate receipts, live-state-unbound post-receipt RNG entry, forged staging
blobs, non-object publication refs, and repeatable incomplete terminal
attestation.

The repair now binds config, preholdout, and holdout tracked-state identities
and the literal analytical manifest to freshly captured disk/Git state at
every boundary and immediately before RNG entry. Receipt payloads and every
cross-binding are validated before exclusive creation; failures preserve
existing bytes and create no new receipt. Config validation requires complete
literal model, estimator, parameter, scenario, seed, gate, artifact, and
boundary-label values.

Nonnested scenarios now have only development 12 and holdout 24. Fit evidence
requires exact scenario split frames, complete duplicate-free arrival pairs,
same-source equal-emission reconstruction, complete zero-driver fit/profile
reconciliation, fully typed failed rows, and the exact 17-column predictive
schema over 27 canonical strata. Local reducers require exact scenario-
specific typed evidence and reject unavailable, contradictory, or forced-
warning states using only canonical local reason domains.

Latent diagnostics derive exact passable, deterministic sparse, and alignment-
score cell frames from the Goal 017 landscape rather than caller nomination;
typed row states remain complete and recommendation-neutral. Fixture dispatch
accepts only its owned side-effect-free service. Staging captures live
worktree/index blobs against the literal allowlist, retry binds the exact
failed command and unchanged envelope, publication checks captured object,
tree, parent, and ref semantics, and terminal attestation binds the complete
observed envelope with exact-once Log/index enforcement. The test file contains
an executable literal manifest of exactly 98 amendment test names.

GREEN and validation evidence on the bound source/test tuple:

- exact executable amendment manifest: `98 passed in 0.63s`;
- complete Goal 023 test file: `297 passed in 703.59s`;
- observation and relevant upstream synth-medium regressions:
  `69 passed in 69.92s`;
- Ruff format check: `PASS`;
- Ruff check: `PASS`;
- mypy: `Success: no issues found in 59 source files`;
- tracked and owned-untracked `git diff --check`: `PASS`;
- Goal/spec body equivalence: `106597` bytes, SHA-256
  `855a3c3291dedf473fc1879601987f6126924e71123e4aa515b86805a3bb93eb`;
- pre-append parent-bound Log chain: `14/14` hashes and `5/5` declared byte
  counts reproduced;
- canonical artifact directory, recovery config, preholdout receipt, and
  holdout receipt: `ABSENT`;
- Git index: `EMPTY`.

Review dispositions for this replacement tuple:

- scientific: `PENDING`
- statistical: `PENDING`
- executor-readiness: `PENDING`
- artifact/schema: `PENDING`
- code: `PENDING`
- provenance/freeze: `PENDING`
- independent max rereview: `PENDING`

No Task 3 scenario, live or production RNG construction, simulation, runtime
benchmark, calibration, canonical artifact/config/receipt, freeze, holdout,
staging, commit, push, publication, cleanup, deletion, reset, or restore
occurred. Required unit tests used only deterministic fixture/test RNG objects
and temporary-directory serializers. This is not acceptance. Task 3 and every
stochastic or irreversible phase remain blocked pending fresh hash-specific
independent review with no Critical or Important finding.

## 2026-07-12 - Integrated Amendment Final Rereview 3 Authority Repair

record_type: `integrated_amendment_final_rereview_3_authority_repair_v1`
parent_line_count: `2666`
parent_byte_count: `132318`
parent_sha256: `f3bc360138e3ce33abf25b741150a7c59dc2daf5dabd9b8c9360a0b9d95df843`
status: `AUTHORITY_REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
acceptance_status: `PENDING`
binding_status: `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`
task_3_authority: `BLOCKED`
calibration_authority: `BLOCKED`
config_emission_authority: `BLOCKED`
freeze_authority: `BLOCKED`
holdout_authority: `BLOCKED`
staging_authority: `BLOCKED`
publication_authority: `BLOCKED`
branch: `codex/spatext-goal023-latent-response-observation-gate`
head: `53462d0365babf2c8070714a930f69b4071af276`
base_ref: `origin/main`
base_commit: `53462d0365babf2c8070714a930f69b4071af276`

This one parent-prefix-bound child repairs C1, I1-I5, M1, and all 15 steps in
`integrated-amendment-final-rereview-3.md`. Every parent byte is preserved as
the exact prefix. The authorized Goal/spec amendment completes external
authority and artifact schemas only. It changes no biological equation,
estimand, generating value, natural support, schedule, effort rule, scenario,
replicate count, threshold, seed mapping, recommendation class, or
transportability statement. Plan, source receipt, dependencies, lockfile, and
observation kernel are unchanged.

Bound hashes before this append:

- Goal: `c20981e0062a03453f99f066cce460e0bcbb2717b803ee009b7e36eb2a9c6af6`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `ffae51c58789fd721032ce734c0ef0250bc2a2727bfbc99530ecd2f16dd20804`
- authoritative spec: `ccd3f601224f36782d44ee43e325214e8ba66928b8e97fc531fe41419341c7d2`
- source: `f18ea913632b07de9f5108bdd23e5ef2a799d20b1a710c6ce5418776e1441e1a`
- tests: `37dee62067c03b8a5e4b47430c1b347f160d5c2580c966644abba66d4cdf2575`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- derived source identity: `6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0`
- final rereview 3: `71fd0e0d242ba4488bc0e8a5fdb54f6290d9b6a77a012cc415fc6fe7f2c05e29`

Behavior-specific RED preceded implementation. The 14 strengthened existing
manifest nodes failed in `1.08s`; direct probes also reproduced acceptance of
12 development plus 12 holdout arrival pairs and found Runbook narrative in
bash block 13. False spec/source tuples passed freeze, created a temporary
receipt before rejection, and returned `CONTINUE_FROZEN_CANDIDATE` at the
pre-RNG list-append spy. No production RNG was constructed.

The repaired authority state machine hashes the live spec, requires the exact
accepted source-receipt file SHA, derives source identity from parsed accepted
landscape/arrival hashes, and binds config, preholdout receipt, holdout
receipt, tracked manifest, and captured state at config, freeze, pre-create,
post-create, and immediate-pre-RNG boundaries. Validation precedes exclusive
creation. Post-create failure preserves bytes and returns an explicit
immutable stop; existing bytes are never replaced.

Successful fit evidence now enforces every natural support, exact boundary
identity, strict rate ordering, and the failed
`equal_rate_mle_noninterior` state. Control reconciliation consumes canonical
24-row zero-driver recovery evidence, returns its canonical decision, and
requires 24 same-source holdout arrival pairs through the complete validator.
Predictive rows implement the available/nonfinite nullable-residual state,
metric domains and algebra, and mandatory warning.

Goal/spec now give complete literal headers, types, nullability, primary keys,
sort keys, and enum domains for `model_parameter_contract.csv` and all six
fit-derived tables that previously relied on unspecified schemas. The private
zero-profile substitute is removed. The Objective bodies are byte-identical
at `117226` bytes with SHA-256
`416890f17cd4ac3ab785dad190b165b05b7a76ae8425e7ab1f51277feccb4282`.

Retry consumes a freshly captured current envelope and one parsed, recomputed,
reviewed Log-only transition bound to the exact failed command. Ordinary Log
append validation no longer trusts a caller boolean. Exact staging captures a
real `git write-tree` identity, and publication transitions consume the
module-issued validated staging identity. Fixture emission accepts only a
module-issued temporary root and rejects the canonical artifact path and
resolved aliases before any write. All 18 Runbook bash fences pass syntax
validation and contain no narrative prose.

GREEN and validation evidence on the bound tuple:

- strengthened counterexample nodes: `14 passed in 0.77s`;
- exact executable amendment manifest: `98 passed in 0.96s`;
- complete Goal 023 test file: `297 passed in 710.36s`;
- observation and relevant upstream synth-medium regressions:
  `69 passed in 46.79s`;
- Ruff format check: `PASS`;
- Ruff check: `PASS`;
- mypy: `Success: no issues found in 59 source files`;
- tracked and owned-untracked diff checks: `PASS`;
- canonical source/frame reconciliation: `5225`, `1306`, and disjoint
  `4180/1045` frames with complete union;
- pre-append Log chain: `15/15` hashes and `6/6` declared byte counts;
- Git index: `EMPTY`;
- canonical artifact directory, recovery config, preholdout receipt, holdout
  receipt, and production Goal 023 CLI: `ABSENT`.

Review dispositions for this authority-repair tuple:

- scientific: `PENDING`
- statistical: `PENDING`
- executor-readiness: `PENDING`
- artifact/schema: `PENDING`
- code: `PENDING`
- provenance/freeze: `PENDING`
- independent max rereview: `PENDING`

No Task 3 command, production RNG/vector, simulation, runtime benchmark,
calibration, canonical artifact/config/receipt, production freeze, holdout,
staging, commit, push, publication, cleanup, deletion, reset, or restore
occurred. Required unit tests used only deterministic test objects,
list-append spies, fake Git runners, and temporary-directory serializers and
receipts. This is not acceptance. Task 3 and every stochastic or irreversible
phase remain blocked pending fresh hash-specific independent max rereview with
no Critical or Important finding.

## 2026-07-12 - Integrated Amendment Final Rereview 4 Repair

record_type: `integrated_amendment_final_rereview_4_repair_v1`
parent_line_count: `2784`
parent_byte_count: `138517`
parent_sha256: `0bbd23f592a57c875e9b12a109c06cedf5912f8eb8697e14ba156bc50966d030`
status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
acceptance_status: `PENDING`
binding_status: `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`
task_3_authority: `BLOCKED`
calibration_authority: `BLOCKED`
config_emission_authority: `BLOCKED`
freeze_authority: `BLOCKED`
holdout_authority: `BLOCKED`
staging_authority: `BLOCKED`
publication_authority: `BLOCKED`
branch: `codex/spatext-goal023-latent-response-observation-gate`
head: `53462d0365babf2c8070714a930f69b4071af276`
base_ref: `origin/main`
base_commit: `53462d0365babf2c8070714a930f69b4071af276`

This one parent-prefix-bound child repairs I1-I5 and all 11 correction steps in
`integrated-amendment-final-rereview-4.md`. Every parent byte is preserved as
the exact prefix. The coordinated Goal/spec amendment completes literal truth,
artifact, command, publication, and terminal authority without changing any
biological equation, estimand, generating value, natural support, schedule,
effort rule, scenario, replicate count, threshold, seed mapping,
recommendation class, or transportability statement. Plan, source receipt,
dependencies, lockfile, and observation kernel are unchanged by this repair.

Bound hashes before this append:

- Goal: `292172dbcdf14d4d44384c630097443a249526fe920a373f741775806f40d5e3`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb`
- authoritative spec: `d5e5b4ca088478fe6c0a95a35aad12698cfc54e949cac001ec6d9b1e3ce21c5f`
- source: `00d4871d7de0447293bd86fcafd960aa3ffe7dbabd15fd45e44600a11656e860`
- tests: `a8ae7c5202d9e4462785a9a62d3a1fade0425a8b28bf8d4e008430283c0c8919`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- derived source identity: `6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0`
- final rereview 4: `b70bf4b331b59ef62fdc73348fb3888e84ec96c554fab67e07ba1c4f9e944749`

Behavior-specific RED preceded implementation. Eight individually executed
existing manifest nodes failed on the fresh counterexamples: forged dense and
null zero-driver truth, nonfinite/negative summaries, alternate config schema
versions, caller Boolean equal-emission statuses, opaque mutating retry/Task 6
commands, distinct-checkout publication, and a newly parented second terminal
record. The failures were behavioral assertions, not missing imports or future
artifacts.

The repaired scientific evidence path freezes one literal
scenario/parameter-truth frame. Every recovery row reconstructs truth from that
frame, reconciles status, variant, estimate, likelihood, starts, and boundary
state to exactly one fit row, and recomputes intervals, coverage, and errors.
Only continuous-abundance recovery rows are truth-free. Complete fit-bound
profile, coverage, predictive, and control-decision validators reject missing,
duplicate, nonfinite, negative, out-of-support, contradictory, or wrong-split
evidence. Zero-driver, arrival, and equal-emission decisions are recomputed from
the canonical emitted recovery and fit rows, including the six fixed status
rows.

Goal/spec and source now transcribe complete `v1` authority for all 22
artifacts: literal enum domains, schema versions, headers, types, row-specific
nullability, keys, sorts, JSON nested keys and string literals, receipt
namespace, report links, and visual source tables. Goal/spec Objective bodies
are byte-identical at `133582` bytes with SHA-256
`5daae64f6464f529d31f41523efd01da05ab5f2aa17eb8c9a8d546749e412007`.

Retry and Task 6 resolve only the exact twelve Runbook section 7 argv vectors,
with command class, parsed phase, and reviewed disposition bound in the failure
and retry records. Staging and publication capture a live Git common object
store and validated `git write-tree`; the real temporary integration exercised
distinct Goal and canonical worktrees through commit, fast-forward merge, and
local push-state transitions. Terminal attestation binds the canonical Log
path, embeds the complete envelope, updates the realistic Log index/cached
state, rejects recursively parented terminal records, and returns the explicit
immutable stop on any post-append mismatch.

GREEN and validation evidence on the bound tuple:

- exact executable amendment manifest: `98 passed in 1.63s`;
- complete Goal 023 test file: `297 passed in 707.02s`;
- observation and relevant upstream synth-medium regressions:
  `69 passed in 46.69s`;
- all `98` proposal names, manifest entries, and AST definitions are exact,
  unique, ordered, and contain executable assertions or rejection checks;
- Ruff format check: `85 files already formatted`;
- Ruff check: `All checks passed!`;
- mypy: `Success: no issues found in 59 source files`;
- tracked and owned-untracked diff checks: `PASS`;
- all `18` Runbook bash blocks parse and all `12` section 7 commands match the
  closed source registry exactly;
- canonical source hashes/counts and the `5225/1306/4180/1045` frames
  independently reconstruct;
- pre-append Log chain: `16/16` hashes and `7/7` byte counts;
- Git index: `EMPTY`; HEAD and `origin/main` remain the pinned commit;
- canonical artifact directory, recovery config, preholdout receipt, holdout
  receipt, production Goal 023 CLI, and remote Goal 023 branch: `ABSENT`.

Review dispositions for this repair tuple:

- scientific: `PENDING`
- statistical: `PENDING`
- executor-readiness: `PENDING`
- artifact/schema: `PENDING`
- code: `PENDING`
- provenance/freeze: `PENDING`
- independent max rereview: `PENDING`

No Task 3 command, production RNG object/vector/payload, simulation, runtime
benchmark, calibration, canonical artifact/config/receipt, production freeze,
holdout, real-project staging, commit, push, publication, cleanup, deletion,
reset, or restore occurred. Required tests used deterministic in-memory data,
spies, fake runners, temporary serializers, and pytest-cleaned temporary Git
repositories only. This is not acceptance. Task 3 and every stochastic or
irreversible phase remain blocked pending fresh hash-specific independent max
rereview with no Critical or Important finding.

## 2026-07-12 - Integrated Amendment Final Rereview 5 Repair

record_type: `integrated_amendment_final_rereview_5_repair_v1`
parent_line_count: `2902`
parent_byte_count: `144896`
parent_sha256: `9b7e9843f0c67cb445b6b90d158fabbf6ce3005f6c487d96e09e9321bbc5d381`
status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
acceptance_status: `PENDING`
binding_status: `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`
task_3_authority: `BLOCKED`
calibration_authority: `BLOCKED`
config_emission_authority: `BLOCKED`
freeze_authority: `BLOCKED`
holdout_authority: `BLOCKED`
staging_authority: `BLOCKED`
publication_authority: `BLOCKED`
branch: `codex/spatext-goal023-latent-response-observation-gate`
head: `53462d0365babf2c8070714a930f69b4071af276`
base_ref: `origin/main`
base_commit: `53462d0365babf2c8070714a930f69b4071af276`

This one parent-prefix-bound child repairs I1-I4 and all ten correction steps
in `integrated-amendment-final-rereview-5.md`. Every parent byte is preserved
as the exact prefix. The coordinated Goal/spec amendment makes the remaining
predictive, science-bundle, profile, control, runtime, and verification
authority literal and executable without changing any frozen biological or
statistical model equation, estimand, generating value, natural support,
scenario, schedule, effort rule, replicate count, threshold, seed mapping,
recommendation class, transportability statement, or publication authority.
Plan, Runbook, source receipt, dependencies, lockfile, and observation kernel
are unchanged by this repair.

Bound hashes before this append:

- Goal: `fcc948d50f95b55ea9cc545bd56c56a3190a03f28a00130b998a67c9966d492f`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb`
- authoritative spec: `d034320882b2fd69076ec9539704369c35bae107c83f531b7c2bf649a8e2e112`
- source: `8ad0c1ea96ea73686a677cc496c3ed1a63584a6787a238b09e0d4d5d1b45a231`
- tests: `7013ccdece7d0ddc15354b8530d636e6b2a71e227d50d58dbb17e5eff528a04e`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- derived source identity: `6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0`
- final rereview 5: `e8b647a66354efb321ef281302a69f8e6bb52a98a5ac1928995fc8bd8fcbb34f`

Behavior-specific RED preceded implementation. The strengthened exact-manifest
nodes T3A-011, T3L-020, T3D-013, T3D-014, T3R-017, and T3S-001 failed `6/6`
on contradictory recovery/profile state, hidden fixture side effects,
caller-selected control/final rows, unrecomputed predictive warning,
availability-precedence, and impossible runtime/verification evidence. A
separate finite high-Stouffer counterexample failed `1/1`. Direct finite
low-Holm and self-certified verification probes also failed their required
rejection assertions. These were behavioral failures against working source,
not import, collection, or missing-artifact failures.

Predictive warning is now exactly incomplete/nonfinite/failed fit, Holm-adjusted
`p < 0.01`, or `abs(Stouffer Z) > 3`, with the gate derived only from the
recomputed warning and exact open boundaries at `0.01` and `3`. One complete
science-bundle validator derives every required scenario/split/variant identity
frame across fit, recovery, profile, coverage, latent, predictive, and control
tables and rejects every missing, extra, duplicate, orphan, or foreign group
before gate reduction.

Successful required fits now consume complete ordered profile groups. Frozen
likelihood-ratio crossing rules derive endpoints, openness, and two-sidedness;
recovery errors, widths, coverage, gates, and summaries are recomputed from
that validated evidence. All 18 control rows are reconstructed from canonical
zero, arrival, alignment, equal-emission, bootstrap, status, scenario-reason,
and reducer evidence, including the retained-observed/failed-bootstrap state.
No caller-selected final row survives reconciliation.

Runtime validation transcribes the complete task-unit authority, reconstructs
the exact 96 calibration and 536 holdout arrays in stable order, applies exact
eight-worker LPT loads, the `1.20` projection, the `1500`-second limits, and
derives `passed`. Verification validates exact manifest-detail schema and live
represented bytes, binds every check to validated source/runtime/receipt/
science/control evidence, and derives recommendation, transportability, and
top-level `passed`. The exact 98 names and order are unchanged; all 98 AST
nodes contain executable assertions or rejection checks.

GREEN and validation evidence on the bound tuple:

- exact executable amendment manifest: `98 passed in 5.13s`;
- complete Goal 023 test file: `297 passed in 708.84s (0:11:48)`;
- observation and relevant upstream synth-medium regressions:
  `69 passed in 45.49s`;
- real temporary two-worktree/publication and terminal integration:
  `2 passed in 1.01s`;
- Ruff format check: `85 files already formatted`;
- Ruff check: `All checks passed!`;
- mypy: `Success: no issues found in 59 source files`;
- tracked and owned-untracked diff checks: `PASS`;
- all `18` Runbook bash blocks parse and all `12` section 7 commands match the
  closed source registry exactly;
- proposal/manifest/AST: `98/98/98`, exact, unique, ordered, with `98/98`
  executable assertion nodes;
- Goal/spec Objective bodies: byte-identical at `140530` bytes;
- source hashes/counts and the `5225/1306/4180/1045` frames independently
  reconstruct with a disjoint `4180/1045` union equal to all passable cells;
- pre-append Log chain: `17/17` hashes and `8/8` declared byte counts;
- Git index: `EMPTY`; HEAD and `origin/main` remain the pinned commit;
- canonical artifact directory, recovery config, preholdout receipt, holdout
  receipt, production Goal 023 CLI, and remote Goal 023 branch: `ABSENT`.

Review dispositions for this repair tuple:

- scientific: `PENDING`
- statistical: `PENDING`
- executor-readiness: `PENDING`
- artifact/schema: `PENDING`
- code: `PENDING`
- provenance/freeze: `PENDING`
- independent max rereview: `PENDING`

No Task 3 production command, production RNG object/vector/payload, simulation,
runtime benchmark, calibration, canonical artifact/config/receipt, production
freeze, holdout, real-project staging, commit, push, publication, cleanup,
deletion, reset, or restore occurred. Required tests used deterministic fixture
data, spies, fake runners, temporary serializers, and pytest-cleaned temporary
Git repositories only. This is not acceptance. Task 3 and every stochastic or
irreversible phase remain blocked pending fresh hash-specific independent max
rereview with no Critical or Important finding.

## 2026-07-12 - Integrated Amendment Final Rereview 6 Repair

record_type: `integrated_amendment_final_rereview_6_repair_v1`
parent_line_count: `3024`
parent_byte_count: `151572`
parent_sha256: `d88afdf3c0bc7bad4e02023cba4c94e0458269e3daf3d85c314ac4997669c999`
status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
acceptance_status: `PENDING`
binding_status: `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`
task_3_authority: `BLOCKED`
rng_construction_authority: `BLOCKED`
calibration_authority: `BLOCKED`
config_emission_authority: `BLOCKED`
freeze_authority: `BLOCKED`
holdout_authority: `BLOCKED`
staging_authority: `BLOCKED`
publication_authority: `BLOCKED`
branch: `codex/spatext-goal023-latent-response-observation-gate`
head: `53462d0365babf2c8070714a930f69b4071af276`
base_ref: `origin/main`
base_commit: `53462d0365babf2c8070714a930f69b4071af276`

This one parent-prefix-bound child repairs I1-I4 and the Complete Repair Gate
in `integrated-amendment-final-rereview-6.md`. Every parent byte is preserved
as the exact prefix. The coordinated Goal/spec amendment and deterministic
fixture-validator repair add persisted design authority and complete predictive
warning provenance without changing any frozen biological or statistical model
equation, estimand, generating value, natural support, scenario, schedule,
effort rule, replicate count, threshold, seed mapping, recommendation class,
transportability statement, or publication authority. Plan, Runbook, source
receipt, dependencies, lockfile, and observation kernel are unchanged by this
repair.

Bound hashes before this append:

- Goal: `03a59a5e0eae6aa8dfd74bf3e4e57550d4bbecef90544540033f1adc96ffe1cf`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb`
- authoritative spec: `e48bf2a18282b2fb4d76429bb551613dcd3d988c137766a579500785b8134fd3`
- source: `6108006d816e7fa5e54a005d1d5d98922b83225fb57578fd4699e79ba001c726`
- tests: `a0d298e3ba885306d21e154e3085a76e5b7cbe08630f14e86cc7886dc358f78c`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- derived source identity: `6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0`
- final rereview 6: `fe8528caada0f314ea7430fe1542a8999bcf9fd0d3b5ba7018d4715636a99451`

Behavior-specific RED preceded implementation. The contradictory converged
`JointFitResult` with a failed plug-in diagnostic was accepted; the persisted
fit artifact lacked the normalized design fields; finite Stouffer and Holm
rejections disappeared from the zero-driver local decision; and forced
nonfinite warnings satisfied each stress warning requirement. These were
working-validator counterexamples, not missing imports, missing artifacts, or
renamed test nodes.

`fit_execution_evidence.csv` is now a literal normalized `v2` table with one
fit-result row and every applicable potential, oracle, and plug-in diagnostic
row per exact fit identity. The complete frame has `990` fit rows and `1695`
design rows. Provenance, role, row and column counts, rank, condition, pass,
typed failure, applicability, nullability, key, sort, report link, visual
dependency, and verification digest are validated from persisted rows. No
design state is inferred from fit success or inserted as a reducer constant.

`JointFitResult` is fail-closed: convergence requires accepted parameters, a
converged multistart, two passing typed diagnostics, and null failure; failed
potential or plug-in design rejects convergence and parameters while retaining
diagnostic audit state and a nonempty typed reason. The live fitter now returns
the exact failed state `joint_plugin_design_gate_failed` when the plug-in gate
fails.

Predictive state is reconstructed separately as
`predictive_complete_finite`, `predictive_pass`, `finite_rule_fired`,
`scientific_warning_available`, and `forced_warning`. Scientific warning
requires complete finite evidence and a finite Holm-adjusted `p < 0.01` or
`abs(Stouffer Z) > 3`; exact `0.01` and `3` remain open boundaries. Forced
evidence takes precedence when both classes coexist and cannot satisfy arrival,
dropout, continuous-abundance, or frailty warning requirements. Zero-driver
exclusion also requires the reconstructed `predictive_pass`.

The complete deterministic science fixture traverses all `990` fit identities,
`1695` design rows, `2340` recovery rows, `11700` profile points, `105`
coverage rows, `552` latent groups, `504` predictive groups, `23` predictive
summary groups, and exactly `18` reconstructed controls. All eleven local
decisions pass and the final recommendation is rank `4`, class
`latent_response_observation_gate_passed`, with verification recommendation
and top-level pass true. One-fact Stouffer, Holm, forced-warning, missing,
duplicate, provenance, role, rank, condition, potential, oracle, and plug-in
mutations fail closed and propagate through local reason, control row, final
rank/class, and verification.

GREEN and validation evidence on the bound tuple:

- exact executable amendment manifest: `98 passed in 738.60s`;
- complete Goal 023 test file: `297 passed in 741.68s`;
- observation and relevant upstream synth-medium regressions:
  `69 passed in 46.65s`;
- real temporary two-worktree/publication and terminal integration:
  `2 passed in 1.12s`;
- Ruff format check: `85 files already formatted`;
- Ruff check: `All checks passed!`;
- mypy: `Success: no issues found in 59 source files`;
- `git diff --check`: `PASS`;
- all `18` Runbook Bash blocks parse and all `12` section 7 commands match the
  closed source registry exactly;
- proposal/manifest/AST: `98/98/98`, exact, unique, ordered, with `98/98`
  executable assertion nodes;
- Goal/spec Objective bodies: byte-identical at `147228` bytes with SHA-256
  `bb97515b8a7769235c33a98abfd5aa6854cd62f2c5c84cabed9ed1e5a164e97a`;
- source hashes/counts and complete science/cell frames independently
  reconstruct, including disjoint `4180/1045` alignment frames whose union is
  all `5225` passable cells;
- pre-append Log chain: `18/18` hashes and `9/9` declared byte counts;
- Git index: `EMPTY`; HEAD and `origin/main` remain the pinned commit;
- canonical artifact directory, recovery config, preholdout receipt, holdout
  receipt, production Goal 023 CLI, and remote Goal 023 branch: `ABSENT`.

Review dispositions for this repair tuple:

- scientific: `PENDING`
- statistical: `PENDING`
- executor-readiness: `PENDING`
- artifact/schema: `PENDING`
- code: `PENDING`
- provenance/freeze: `PENDING`
- independent max rereview: `PENDING`

No Task 3 production command, production RNG object/vector/payload, simulation,
runtime benchmark, calibration, canonical artifact/config/receipt, production
freeze, holdout, real-project staging, commit, push, publication, cleanup,
deletion, reset, or restore occurred. Required tests used deterministic fixture
data, spies, fake runners, temporary serializers, and pytest-cleaned temporary
Git repositories only. This is not acceptance. Task 3 and every stochastic or
irreversible phase remain blocked pending fresh hash-specific independent max
rereview with no Critical or Important finding.

## 2026-07-12 - Integrated Amendment Final Rereview 7 Repair

record_type: `integrated_amendment_final_rereview_7_repair_v1`
parent_line_count: `3157`
parent_byte_count: `158768`
parent_sha256: `a65439ece9b807e4186183a9996e9d967c213da86c618864ee2f997622a848a6`
status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
acceptance_status: `PENDING`
binding_status: `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`
scientific_review: `PENDING`
statistical_review: `PENDING`
executor_readiness_review: `PENDING`
artifact_schema_review: `PENDING`
code_review: `PENDING`
provenance_freeze_review: `PENDING`
independent_max_rereview: `PENDING`
task_3_authority: `BLOCKED`
rng_construction_authority: `BLOCKED`
vector_payload_authority: `BLOCKED`
simulation_authority: `BLOCKED`
benchmark_authority: `BLOCKED`
calibration_authority: `BLOCKED`
artifact_authority: `BLOCKED`
config_emission_authority: `BLOCKED`
receipt_authority: `BLOCKED`
freeze_authority: `BLOCKED`
holdout_authority: `BLOCKED`
staging_authority: `BLOCKED`
commit_authority: `BLOCKED`
push_authority: `BLOCKED`
publication_authority: `BLOCKED`
branch: `codex/spatext-goal023-latent-response-observation-gate`
head: `53462d0365babf2c8070714a930f69b4071af276`
base_ref: `origin/main`
base_commit: `53462d0365babf2c8070714a930f69b4071af276`

This one parent-prefix-bound child repairs I1-I4 and M1 in the authoritative
SHA-256-specific `integrated-amendment-final-rereview-7.md`. Every parent byte
is preserved as the exact prefix. Goal and authoritative spec were amended
byte-identically from `## Objective`; source, assigned tests, and the stale
proposal behavior were repaired. Plan, Runbook, source receipt, artifact count,
biological model, estimands, natural supports, generating values, schedules,
effort rules, seeds, thresholds, scenarios, recommendation classes,
transportability, and publication authority are unchanged.

Bound hashes before this append:

- Goal: `a99909b344cbf8f342a443112d06b38e30ec10e514f6d9e4966cb4c0ab5cf759`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb`
- authoritative spec: `b22d796375ce507317a35a7e6156dcdb138c182f4cb9a35f7dfc3e103ef6dffc`
- source: `973ed93a7165e78ba267f0d3a87b24065a7448b70aed713b22bf1558efd81b0b`
- tests: `bc6827f5fce8ef73d7776771d0eeaf6abf4d82ef3c1aa5f70d023c1020cfc2b4`
- proposal: `7a2fea9874f69aeef07d074c9e217b62aabc7507a8e9ad728e5d707963716b97`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- derived source identity: `6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0`
- final rereview 7: `6439d8235ce469e1a103df9560b217109ec5fb16db40062471cad9f4e26042e3`

Behavior-specific RED preceded implementation. T3A-007 observed arrival
potential authority `104500` instead of fit-only `83600`; T3A-011 accepted a
successful fit with a failed decisive design; T3D-014 accepted predictive
`sample_size=999999`. The combined run produced three intended failures in
`714.04s`, exit `1`, JUnit SHA-256
`56aec63d65b70dc44058faa4b7cdabb3f5854ab81488e98b839c1c52c5c32f5b`.

Arrival potential and plug-in diagnostics now use exactly the 4180 fit-cell
identities and 83600 fit rows, with persisted cell-count and digest evidence.
The 1045 score cells remain score/predictive only. A one-cell fit/score swap,
wrong digest/count, or 104500-row arrival mutation fails before reduction.

`DesignDiagnostic` now owns the exact builtin type, positive dimension,
rank/condition, derived pass, and failure-nullability algebra. Joint and
process-oracle result constructors invoke it and reject forged rank/pass,
condition/pass, NaN/nonfinite, invalid-dimension, and contradictory failure
states. Persisted fit/design evidence is partitioned by exact fit identity and
then checked by an applicability-aware state machine. Failed potential,
joint-fit, process-oracle-fit, plug-in, and oracle states have exact failed or
not-evaluated transitions. Impossible fit/design combinations cannot reach a
scenario reason, control row, recommendation, or verification document.

Predictive rows now carry exact opportunity-frame count and SHA-256 plus the
fixed dropout-mask SHA-256 where applicable. All three metrics in each stratum
share the exact reconstructed retained-frame `n`. Arrival uses score cells;
informative dropout binds its fixed deterministic fixture mask. Size, digest,
metric-disagreement, fit/score-frame, and dropout-mask mutations fail before
summary or recommendation. The existing artifact registry remains exactly 22
paths; the predictive evidence is normalized inside the existing predictive
artifact. The complete fixture no longer uses `n=2`.

M1 is superseded in place: T3A-005 now describes the exact 35-column,
seven-part normalized fit/design behavior while retaining its name and exact
position in the 98-node manifest.

GREEN and validation evidence on the bound tuple:

- exact executable amendment manifest: `98 passed in 745.50s`;
- complete Goal 023 test file: `297 passed in 750.21s` with `--no-cov`;
- observation and relevant upstream synth-medium regressions:
  `69 passed in 46.74s`;
- real temporary two-worktree/publication and terminal integration:
  `2 passed in 1.38s`;
- Ruff format/check and mypy on repaired source/tests: `PASS`;
- `git diff --check`: `PASS`;
- proposal/manifest/AST remains exact `98/98/98`, unique and ordered;
- Goal/spec Objective bodies are byte-identical at `151187` bytes with
  SHA-256 `815c0109f13b846b5a66cb00184384559ba7299e6c91af70d90a4d09248e065c`;
- complete fixture retains 990 fit identities, 1695 design rows, 2340
  recovery rows, 11700 profile points, 105 coverage rows, 552 latent groups,
  504 predictive groups, 23 predictive-summary groups, 18 controls, all 11
  local passes, rank 4, `latent_response_observation_gate_passed`, and true
  recommendation/verification;
- source receipt and derived source identities remain exact;
- Git index is empty; HEAD and `origin/main` remain pinned and equal;
- canonical artifacts, config, receipts, production CLI, remote Goal 023
  branch, staging, commits, pushes, and publication remain absent.

No production CLI, RNG object, vector, payload, simulation, runtime benchmark,
calibration, canonical artifact/config/receipt, freeze, holdout, real-project
staging, commit, push, cleanup, reset, restore, deletion, or publication was
performed. Deterministic fixtures, fake runners, temporary serializers, and
pytest-cleaned temporary Git repositories were the only execution surfaces.
This is a repair result, not acceptance. Task 3 and every stochastic or
irreversible authority remain blocked pending fresh hash-specific independent
max rereview with zero Critical and zero Important findings.

## 2026-07-12 - Integrated Amendment Final Rereview 8 Repair

record_type: `integrated_amendment_final_rereview_8_repair_v1`
parent_line_count: `3282`
parent_byte_count: `165543`
parent_sha256: `02f94a646d75557afe92f944fc82eb8869d452c28a7a42d94fdc044c820cc6a3`
status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
acceptance_status: `PENDING`
binding_status: `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`
scientific_review: `PENDING`
statistical_review: `PENDING`
executor_readiness_review: `PENDING`
artifact_schema_review: `PENDING`
code_review: `PENDING`
provenance_freeze_review: `PENDING`
independent_max_rereview: `PENDING`
task_3_authority: `BLOCKED`
rng_construction_authority: `BLOCKED`
vector_payload_authority: `BLOCKED`
simulation_authority: `BLOCKED`
benchmark_authority: `BLOCKED`
calibration_authority: `BLOCKED`
artifact_authority: `BLOCKED`
config_emission_authority: `BLOCKED`
receipt_authority: `BLOCKED`
freeze_authority: `BLOCKED`
holdout_authority: `BLOCKED`
staging_authority: `BLOCKED`
commit_authority: `BLOCKED`
push_authority: `BLOCKED`
publication_authority: `BLOCKED`
branch: `codex/spatext-goal023-latent-response-observation-gate`
head: `53462d0365babf2c8070714a930f69b4071af276`
base_ref: `origin/main`
base_commit: `53462d0365babf2c8070714a930f69b4071af276`

This one parent-prefix-bound child repairs all four Important findings in the
authoritative SHA-256-specific
`integrated-amendment-final-rereview-8.md`. Every parent byte is preserved as
the exact prefix. Goal and authoritative spec were amended byte-identically
from `## Objective`; source, assigned tests, and the superseded proposal
behavior were repaired. Plan, Runbook, source receipt, exact 22-artifact count,
biological model, estimands, natural supports, generating values, schedules,
effort rules, seeds, thresholds, scenarios, recommendation classes,
transportability, and publication authority are unchanged.

Bound hashes before this append:

- Goal: `076ad8cc29dc08837a985eb169be3ee0113ef1d66ebdcf250b766bb20f98089b`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb`
- authoritative spec: `153658d517b589f9e8e9ea3e04f97c2c6b8c6576baf44a081b98562f9fabd67c`
- source: `40246f46a5fcd80ddae55b0739dde8104b10dc7e2508400f7ee4793c62bea8b7`
- tests: `44eaab1b5be36f9743ae397f0dd13915cd1c12c11107135b4b9f0f145b539062`
- proposal: `89a90783c33d1c571537876fa8d5263d3d8fc61cc0c3b22c407f3a9c4a772e4f`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- derived source identity: `6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0`
- final rereview 8: `c85fe1cca10f3dd31145bbd4354484ad3e5e933a3b9fe2df8736c792c770a367`

Behavior-specific RED preceded source implementation. T3A-011 showed that
exactly 1045 arrival score-cell histories reached the injected optimizer and
returned a converged fit; T3D-014 showed the predictive base record lacked
effort, quality/time label swaps retained the same digest, and no production
adapter existed. The two assigned nodes failed in `772.46s`, exit `1`, with
JUnit SHA-256
`b2834e2b3aa84a08ee2e4512857688952187322529a6be213914e5d72057b81b`.
The same assigned nodes also carry the impossible-dimension and complete-bundle
transition probes required by the rereview.

I1 is closed by a module-issued immutable `AnalystFitFrame` derived from exact
canonical IDs. The joint fitter requires that frame and rejects history IDs
before potential design or objective evaluation. `JointFitResult` carries the
issued frame, count, and digest, and persisted joint design fields derive only
from that validated result. Arrival admits exactly 4180 fit cells and 83600
potential/plug-in rows. Score histories, fit/score substitutions, and the
5225-cell/104500-row mutation cannot reach optimization or reduction.

I2 is closed by the authoritative design invariant
`rank <= min(n_rows,n_columns)` and pass requirement
`n_rows >= n_columns`. Potential, plug-in, and oracle `1x3/rank3` and
`2x3/rank3` states are rejected; each `3x3/rank3` control is valid. The same
algebra is enforced by typed constructors and persisted rows.

I3 is closed by nine frozen typed failure classes and one explicit transition
table. Potential failure forbids optimizer-result fields. Optimizer/nonfinite
failure requires rank-zero joint/process failure diagnostics. Evaluated rank or
condition diagnostics require the matching plug-in or oracle gate class, and
the observation/equal-rate applicability exceptions are explicit. Every
persistable transition is exercised against the complete 990-fit/1695-design
bundle before reduction; the old optimizer-failure plus evaluated-rank
contradiction now fails closed.

I4 is closed by one module-issued predictive frame adapted from the exact
canonical `ScheduledOpportunity` tuple. Its canonical serialization covers
cell ID, time, `float.hex()` effort, quality stratum, time band, keyed keep
identity, and keep/drop state in canonical order. Sample sizes, digest, and all
three metrics per stratum derive from the same retained objects consumed by the
metric calculation. Equal-cardinality quality/time swaps, effort mutation,
metric-specific size/digest changes, fit/score-frame changes, and keyed mask
swaps fail before summary or recommendation. The production adapter is tested;
the artifact registry remains exactly 22 paths.

The proposal now fully supersedes both its original 23-column/five-part and
intermediate 35-column behavior. T3A-005 binds the exact v3 36-column,
seven-part, typed-failure/result-derived-frame contract while retaining its
assigned name and exact position in the 98-node manifest.

GREEN and validation evidence on the bound tuple:

- exact executable amendment manifest: `98 passed in 817.48s` with `--no-cov`;
- complete Goal 023 test file: `297 passed in 818.38s` with `--no-cov`;
- observation and relevant upstream synth-medium regressions:
  `69 passed in 49.89s` with `--no-cov`;
- real temporary two-worktree/publication and terminal integration:
  `2 passed in 1.59s` with `--no-cov`;
- Ruff format: `85 files already formatted`;
- Ruff check: `All checks passed!`;
- mypy: `Success: no issues found in 59 source files`;
- `git diff --check`: `PASS`;
- exact Goal/spec Objective bodies: `156188` bytes, SHA-256
  `756b9edc86b1bded55714a891c0ab4669624fb22415685b01c3894610c3bec52`;
- complete fixture retains 990 fit identities, 1695 design rows, 2340 recovery
  rows, 11700 profile points, 105 coverage rows, 552 latent groups, 504
  predictive groups, 23 predictive-summary groups, 18 controls, all 11 local
  passes, rank 4, `latent_response_observation_gate_passed`, and true
  recommendation/verification;
- source receipt and derived source identities remain exact;
- Git index is empty; HEAD and `origin/main` remain pinned and equal;
- canonical artifacts, config, receipts, production CLI, remote Goal 023
  branch, staging, commits, pushes, and publication remain absent.

No production CLI, RNG object, vector, payload, simulation, runtime benchmark,
calibration, canonical artifact/config/receipt, freeze, holdout, real-project
staging, commit, push, cleanup, reset, restore, deletion, or publication was
performed. Deterministic in-process fixtures, fake runners, temporary
serializers, and pytest-cleaned temporary Git repositories were the only
execution surfaces. This is a repair result, not acceptance. Task 3 and every
stochastic or irreversible authority remain blocked pending fresh
hash-specific independent max rereview with zero Critical and zero Important
findings.
