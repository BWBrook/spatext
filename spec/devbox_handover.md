# Dev-Box Handover

Date: 2026-05-26

This document is for the counterpart agent taking over `spatext` work on the
Mac Mini development box. It summarizes the current repo state, the scientific
and engineering decisions already made, the ignored artifacts that may need to
be regenerated or copied, and the safest way to resume work.

## Current Git State

Canonical repository:

```text
https://github.com/BWBrook/spatext.git
```

Latest verified commit at handover:

```text
f639afd9fd5a2eaf7fd767218749df9e9ee13d96
Implement and revise synth-small predator truth workflow
```

The WSL checkout at `/home/bwbrook/papers/spatext` was clean and aligned with
`origin/main` when this document was created.

The Mac Mini SSH alias from WSL is:

```text
dev-box-ts
```

Alias details from the current WSL SSH config:

```text
Host dev-box-ts barrys-mac-mini
HostName 100.86.240.85
User bwbrook
IdentityFile ~/.ssh/id_ed25519_mac_mini
```

A bounded SSH probe on 2026-05-26 reached the Mac Mini:

```text
host=Mac-mini.lan
home=/Users/bwbrook
```

No existing `spatext` checkout was found under common locations such as
`/Users/bwbrook/papers/spatext`, `/Users/bwbrook/work/spatext`, or
`/Users/bwbrook/git/spatext`.

## First Dev-Box Steps

On the Mac Mini, clone the repository if it is absent:

```bash
mkdir -p /Users/bwbrook/papers
cd /Users/bwbrook/papers
git clone https://github.com/BWBrook/spatext.git
cd spatext
```

If the repository already exists elsewhere, use that checkout instead and
fast-forward it:

```bash
git fetch origin --prune
git checkout main
git pull --ff-only origin main
git rev-parse HEAD
```

The expected head is:

```text
f639afd9fd5a2eaf7fd767218749df9e9ee13d96
```

Then install and verify the Python environment:

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

The project requires CPython `3.14.4`, pinned in `.python-version`. The package
requires `>=3.14,<3.15`, so if `uv sync` complains, install or expose that
Python version first.

## Repo Operating Rules

Read these files first:

```text
AGENTS.md
README.md
spec/problem_statement.md
spec/theory.md
spec/report_log.md
```

Important operating conventions:

- `spec/` is the current design authority.
- The code architect agent is called `spat` in repo docs.
- Use `uv` as the single Python environment and dependency manager.
- Keep core package code in `src/spatext/`.
- Keep tests in `tests/`.
- Keep small command-line utilities in `scripts/`.
- Do not commit or push unless Barry explicitly asks.
- Prefer bundled commits over highly atomic commits.
- Update `spec/report_log.md` after meaningful work.
- After substantial implementation, review `README.md` and `AGENTS.md` and
  update them if the repo behavior, commands, or module status changed.

## Scientific Mission

`spatext` is a response-only spatiotemporal extinction inference project.

The core scientific aim is to ask what can be inferred about a spreading
extinction driver when direct driver observations are sparse, biased, or absent,
and the main available evidence is the biological response.

Two central latent quantities anchor the project:

```text
T_P(x): driver arrival time at location x
T_X(x): extirpation time at location x
```

The first applied motivation is the mink-water-vole system in Great Britain and
Ireland, but the repo should remain a general framework rather than a
single-case script pile.

Synthetic validation is a hard gate before real-data interpretation. Failure,
weak signal, or non-identifiability are legitimate scientific outcomes and
should be surfaced explicitly.

## Implemented Module State

### Package And Tooling

The repo is an installable Python package using:

```text
src/spatext/
pyproject.toml
uv.lock
pytest + coverage
ruff
mypy
pre-commit
```

The current test suite had 24 passing tests and coverage above the configured
90% threshold when last verified.

### `synth-small` Baseline

Spec:

```text
spec/synth_small_baseline.md
```

Implementation:

```text
src/spatext/spatial.py
src/spatext/synth/small/baseline.py
scripts/build_synth_small_baseline.py
tests/test_spatial.py
tests/test_synth_small_baseline.py
```

Purpose:

- build a `25 x 25` square-lattice synthetic domain,
- construct deterministic suitability and carrying-capacity surfaces,
- compute prey-only equilibrium abundance,
- emit a disk artifact bundle for audit and later modules.

Build command:

```bash
uv run python scripts/build_synth_small_baseline.py \
  --output-dir artifacts/synth_small_baseline
```

### `synth-small` Inspection

Spec:

```text
spec/synth_small_inspection.md
```

Implementation:

```text
src/spatext/synth/small/inspect.py
scripts/inspect_synth_small_baseline.py
tests/test_synth_small_inspection.py
```

Purpose:

- reload a baseline artifact bundle from disk,
- verify structural and numerical contracts,
- produce parameter and surface-summary tables,
- write a Markdown report under `inspection/`.

Inspection command:

```bash
uv run python scripts/inspect_synth_small_baseline.py \
  --artifact-dir artifacts/synth_small_baseline
```

### First Baseline Review Bundle

Spec:

```text
spec/synth_small_first_review_run.md
```

This was an execution spec for creating the first canonical baseline review
bundle at:

```text
artifacts/synth_small_first_review
```

That directory is ignored by Git and should be regenerated or copied if needed.

### Deterministic Predator-Truth Module

Spec:

```text
spec/synth_small_predator_truth.md
```

Implementation:

```text
src/spatext/synth/small/predator.py
scripts/build_synth_small_predator_truth.py
tests/test_synth_small_predator_truth.py
```

Purpose:

- generate driver arrival `T_P(x)`,
- generate time-varying predator pressure `P_t(x)`,
- simulate prey abundance trajectory `N_t(x)`,
- compute latent true extirpation `T_X^true(x)`,
- compute extirpation lag `T_X^true(x) - T_P(x)`,
- emit a full deterministic truth bundle.

Build command:

```bash
uv run python scripts/build_synth_small_predator_truth.py \
  --output-dir artifacts/synth_small_predator_truth
```

Current default interpretation:

- exogenous generalist predator,
- west-to-east arrival from the western boundary,
- bounded post-arrival pressure ramp,
- Type II per-capita prey mortality,
- absolute quasi-extinction threshold,
- no default Allee effect in deterministic v1.

Current default parameters of scientific note:

```text
introduction_time = 4
front_speed_cells_per_step = 1.0
ramp_duration = 8
predation_scale = 1.0
half_saturation = 6.0
quasi_extirpation_abundance = 3.0
post_arrival_buffer = 24
```

Current canonical predator-truth run outcome:

```text
predation_response_form = type_ii
extirpation_threshold_form = absolute_quasi_extinction
extirpated_fraction = 0.4032
surviving_fraction = 0.5968
driver_arrival range = 4 to 28
true_extirpation range = 15 to 52
finite lag range = 11 to 41
stayed_finite = true
stayed_nonnegative = true
used_nonnegative_clipping = false
```

Important scientific decision:

The first predator-truth implementation used a Type III response and a local
threshold `min(phi K(x), rho N0(x))`. Artifact review showed that this encoded
a scarcity refuge: naturally sparse cells were less likely to extirpate than
denser cells. Barry and spat agreed that this was undesirable for the current
generalist-predator story. The default was revised to Type II mortality plus an
absolute quasi-extinction threshold. Type III remains conceptually useful for
later constrained/prey-switching scenarios, but it is not the current default.

See `spec/report_log.md`, especially Interaction 18, for the decision trail.

## Artifact Policy For The Dev Box

`artifacts/` is intentionally ignored by Git. The source code and specs are in
Git; the generated review bundles are not.

Currently present WSL artifact directories:

```text
artifacts/synth_small_first_review      about 360K
artifacts/synth_small_predator_truth    about 700K
```

Recommended default on the Mac Mini:

Regenerate artifacts after the repo is fast-forwarded and `uv sync` succeeds.
The bundles are small, deterministic, and quick to produce.

```bash
uv run python scripts/build_synth_small_baseline.py \
  --output-dir artifacts/synth_small_first_review

uv run python scripts/inspect_synth_small_baseline.py \
  --artifact-dir artifacts/synth_small_first_review

uv run python scripts/build_synth_small_predator_truth.py \
  --output-dir artifacts/synth_small_predator_truth
```

If exact continuity with the WSL-generated SVG/NPZ/CSV files is needed, copy
the ignored artifact directories from WSL after the Mac Mini checkout exists.
Assuming the dev-box repo is at `/Users/bwbrook/papers/spatext`, run from WSL:

```bash
ssh -o BatchMode=yes dev-box-ts 'mkdir -p /Users/bwbrook/papers/spatext/artifacts'
rsync -az \
  artifacts/synth_small_first_review \
  artifacts/synth_small_predator_truth \
  dev-box-ts:/Users/bwbrook/papers/spatext/artifacts/
```

After either regeneration or copy, useful files for manual review are:

```text
artifacts/synth_small_first_review/inspection/report.md
artifacts/synth_small_first_review/inspection/verification.json
artifacts/synth_small_predator_truth/summary.json
artifacts/synth_small_predator_truth/diagnostics.json
artifacts/synth_small_predator_truth/driver_arrival.svg
artifacts/synth_small_predator_truth/true_extirpation.svg
artifacts/synth_small_predator_truth/extirpation_lag.svg
artifacts/synth_small_predator_truth/final_abundance.svg
```

## Suggested Resumption Point

The next agent should not restart the project from scratch. The best first move
is:

```bash
git fetch origin --prune
git pull --ff-only origin main
uv sync --all-groups
uv run pytest
uv run python scripts/build_synth_small_predator_truth.py \
  --output-dir artifacts/synth_small_predator_truth
```

Then inspect the regenerated predator-truth artifacts with Barry. The latest
scientific question at hand was whether the revised Type II plus
quasi-extinction default now has the right qualitative spatial pattern, or
whether the deterministic truth benchmark needs gentler tuning before adding
the observation layer.

Likely next work packages:

- build a predator-truth inspection layer analogous to the baseline inspection
  layer,
- add a synthetic observation model over `N_t(x)` and/or `T_X^true(x)`,
- define reconstructed `T_X^obs(x)` from sparse observations,
- create parameter/tuning sweeps for Type II versus later Type III scenarios,
- add a formal artifact report for predator-truth bundles.

## Watch Points

- Do not silently change the predator-truth defaults; if they change, update
  `spec/synth_small_predator_truth.md` and `spec/report_log.md`.
- Keep generated artifacts out of Git unless Barry explicitly asks otherwise.
- Do not add notebooks, `pixi`, or alternative dependency managers without a
  new spec or explicit approval.
- Disk-first verification is an established project pattern.
- Treat equivocal or negative inference outcomes as results, not failures to
  hide.
