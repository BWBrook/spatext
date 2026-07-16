# Goal 023 Task 2a2 Evidence Report

status: `DONE`
date: `2026-07-11`
worktree: `/Users/bwbrook/.codex/worktrees/spatext/goal023`
branch: `codex/spatext-goal023-latent-response-observation-gate`
HEAD: `53462d0365babf2c8070714a930f69b4071af276`

## Scope And Parent Verification

The brief was read before implementation. Only the owned source, test, append-only
ledger, and this ignored report were edited.

Verified before the first edit:

```text
authoritative spec SHA-256  0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d
accepted Task 2a1 source    78169d0114029287fd9a81bd5024b632a4060a8b27b8a14839d616a85d35bdb1
accepted Task 2a1 tests     5321062bfe52574ee34c39d028ff6b6e01f85dce696f7b66f99855204ba4a223
Log parent line count       1962
Log parent SHA-256          b047ab616b7292661b311c3ad227543df3556ad2dbcd9c9117257a60f92f4aad
```

The spec remained byte-identical. The Log parent was rechecked immediately before
the single append.

## Strict TDD Evidence

All Task 2a2 tests were added and formatted before any production-source change.
At RED the accepted source still had its exact Task 2a1 hash.

```text
RED test SHA-256:
159e9baabf34f9bead1458514094e00242b5544c14bc8c995d11122441aa76c6

Command:
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov

Result:
exit 1
123 collected
21 failed, 99 passed, 3 errors in 0.67s
```

All failures/errors were caused by deliberately missing Task 2a2 symbols. The
accepted Task 2a1 cases remained green.

A self-review found the timing-only equal-emission development exception needed
base `process` and `observation` payload indices `0..23`, while predictive/PIT
scientific indices remain `0..11`. A second test-first run produced:

```text
exit 1
1 failed, 122 passed in 1.03s
```

The minimum component-specific validator change then made that cycle green.

## Implemented Outcomes

1. RNG payloads

- Exact seven-key schema and exact primitive/literal checks.
- Unknown keys, scenarios, splits, components, combinations, and non-holdout
  replicate/draw ranges fail before `SeedSequence` construction.
- Compact sorted-key ASCII JSON with no whitespace.
- SHA-256 digest split into eight consecutive big-endian `uint32` words.
- `SeedSequence` plus `Generator(PCG64DXSM(...))`.
- Both frozen development/calibration first-three-`uint64` vectors reproduce
  exactly.
- Holdout construction remains hard-locked; no holdout payload was created or
  inspected.

2. Deterministic simulation

- Process simulation requests one C-order float64 array of shape
  `(n_passable, 20)` and applies absorption only after the full draw exists.
- Every post-absorption uniform remains consumed.
- Returned cell IDs, 21-time state matrix, and transition/censor vector have exact
  shapes/dtypes and immutable byte-buffer storage.
- Observation simulation constructs the full canonical mean vector and makes
  exactly one Poisson call, without state-dependent opportunity skipping.
- The returned analyst histories contain only analyst-visible fields; truth stays
  in the separate evaluator-only process result.

3. Canonical design primitives

- All eleven scenario-to-schedule/effort definitions are literal.
- Dense, structured, and sparse schedules are ordered by integer `cell_id`, then
  ascending time.
- Structured effort is exactly
  `0.7 + 0.6 * min(max((Q + 2) / 4, 0), 1)`.
- Canonical schedule counts reproduced: dense `5225 * 21`, structured
  `5225 * 11`, sparse `1306 * 6`.
- Sparse frame: independent SHA-256 ranking, exactly 1306 of 5225 cells.
- Quality quintiles: exact `(Q, cell_id)` ranking, 1045 cells in each quintile.
- Arrival permutation: row-band by quality-quintile blocks, complete-value cyclic
  shift including nonfinite arrivals.
- Alignment frame: independent SHA-256 ranking, 1045 score and 4180 fit cells.

4. Provenance-separated diagnostics

- `potential_design`: `ANALYST-PREFLIGHT`.
- `process_oracle_truth_at_risk`: `ORACLE-BENCHMARK-ONLY`.
- `joint_plugin_smoothed_at_risk`: `ANALYST-JOINT-PRACTICAL`.
- Generalized float64 SVD uses the frozen `max(n_rows, n_columns)` tolerance,
  full-column-rank condition convention, and `1e8` gate.
- Plug-in interval weights sum normalized analyst-only event paths `k >= j` plus
  censoring and weight every `[1,G,Q]` row by `sqrt(W)`.
- Failed/nonfinite joint fit is represented by an explicit failed plug-in
  diagnostic; oracle truth has no joint interface.

5. Boundary enforcement

- No transform, Halton start, optimizer, inverse audit, profile, scenario runner,
  CLI, artifact writer, calibration run, or holdout implementation was added.
- Source scan found no `scipy.optimize`, `minimize`, `brentq`, `qmc.Halton`,
  artifact path, or holdout receipt reference.
- No artifact directory, preholdout receipt, holdout receipt, or Goal 023 CLI
  exists.
- Nothing was staged, committed, pushed, or published.

## Final Validation

```text
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov
123 passed in 0.63s

uv run pytest tests/test_observe.py --no-cov
48 passed in 0.14s

uv run pytest tests/test_synth_medium_landscape.py --no-cov
5 passed

uv run pytest tests/test_synth_medium_spread_impact.py --no-cov
5 passed

uv run pytest tests/test_synth_medium_observation_design.py --no-cov
5 passed

uv run pytest tests/test_synth_medium_recoverability_target_observation_design.py --no-cov
6 passed

uv run ruff format --check tests/test_synth_medium_latent_response_observation_recovery.py src/spatext/synth/medium/latent_response_observation_recovery.py
2 files already formatted

uv run ruff check tests/test_synth_medium_latent_response_observation_recovery.py src/spatext/synth/medium/latent_response_observation_recovery.py
All checks passed!

uv run mypy src tests
Success: no issues found in 59 source files

git diff --check
exit 0; no output
```

## Final Hashes

```text
source  b61a3f7186a20748dc853f9f7fce8e3a04d008594ad2b64ce0139cebe1980486
tests   921775bf7c9516d7df0749e6e61a1c315c0b1aa7e80a9c05a364f26dc31bc286
Log     4f1773f513e35378a5126772d37c3f86c0cf69ea8560b81ebe4720ed622461e8
spec    0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d
```

Final Log root: `1-2042` at
`4f1773f513e35378a5126772d37c3f86c0cf69ea8560b81ebe4720ed622461e8`.

## Concerns

None within Task 2a2. Independent review remains the orchestrator's next gate;
this implementation did not claim or perform that separate disposition.
