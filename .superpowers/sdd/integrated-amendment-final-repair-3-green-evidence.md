# Integrated Amendment Final Repair 3: GREEN Evidence

Date: `2026-07-12`
Profile: `sol_high_specialist`
State: repair complete; all reviews and acceptance pending; Task 3 blocked

## Test Matrix

- Strengthened behavior-specific nodes: `14 passed in 0.77s`, exit `0`.
- Exact executable 98-name manifest: `98 passed in 0.96s`, exit `0`.
- Complete Goal 023 test file: `297 passed in 710.36s (0:11:50)`, exit `0`.
- Observation and relevant upstream synth-medium regressions:
  `69 passed in 46.79s`, exit `0`.

The exact manifest command was:

```bash
uv run python -c 'import runpy,pytest; p="tests/test_synth_medium_latent_response_observation_recovery.py"; n=runpy.run_path(p)["AMENDMENT_TEST_NAMES"]; raise SystemExit(pytest.main([*(f"{p}::{x}" for x in n), "--no-cov", "-q"]))'
```

The upstream command covered `tests/test_observe.py`,
`tests/test_synth_medium_landscape.py`,
`tests/test_synth_medium_spread_impact.py`,
`tests/test_synth_medium_observation_design.py`, and
`tests/test_synth_medium_recoverability_target_observation_design.py`.

## Static And Authority Checks

- Ruff format check: `2 files already formatted`.
- Ruff check: `All checks passed!`.
- mypy: `Success: no issues found in 59 source files`.
- tracked `git diff --check`: pass.
- owned-untracked source/test `git diff --no-index --check`: no whitespace
  diagnostics; exit `1` only because each complete file is new to Git.
- Goal/spec Objective bodies: byte-identical, `117226` bytes, SHA-256
  `416890f17cd4ac3ab785dad190b165b05b7a76ae8425e7ab1f51277feccb4282`.
- Runbook: all `18` executable bash blocks pass `bash -n`; the moved narrative
  sentence is outside every executable block.
- Live spec SHA-256:
  `ccd3f601224f36782d44ee43e325214e8ba66928b8e97fc531fe41419341c7d2`.
- Derived source SHA-256:
  `6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0`.
- Exact accepted source-receipt file SHA-256:
  `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`.
- Canonical frames: `5225` unique passable cells, `1306` deterministic sparse
  cells, and disjoint `4180` fit plus `1045` score cells with union `5225`.
- Pre-append Log chain: `15/15` parent hashes and `6/6` declared byte counts
  reproduce.
- HEAD and `origin/main` remain
  `53462d0365babf2c8070714a930f69b4071af276`; Git index is empty.

## No Exposure

The canonical artifact directory, recovery config, preholdout receipt,
holdout receipt, and production Goal 023 CLI remain absent. No Task 3 command,
production RNG/vector, simulation, runtime benchmark, calibration, canonical
artifact/config/receipt, production freeze, holdout, staging, commit, push,
cleanup, reset, restore, or repository-file deletion occurred. Unit tests used
only deterministic test objects, list-append spies, fake Git runners, and
temporary-directory serializers/receipts.
