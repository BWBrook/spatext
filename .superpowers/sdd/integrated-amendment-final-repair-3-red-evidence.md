# Integrated Amendment Final Repair 3: RED Evidence

Date: `2026-07-12`
Profile: `sol_high_specialist`
State: pre-implementation RED; Task 3 and stochastic/irreversible phases blocked

## Strengthened Manifest Nodes

The behavior-specific selection covered 14 existing names from the exact
98-node amendment manifest. Command: `uv run pytest --no-cov -q` followed by
the exact node IDs for T3A-005, T3D-013, T3D-014, T3S-004, T3S-009, T3S-010,
T3P-001, T3P-004, T3P-009, T3P-010, T3P-011, T3P-012, T3P-016, and T3P-017.

Observed result: `14 failed in 1.08s`, exit `1`.

Behavior-specific failures included:

- out-of-support successful estimates did not raise;
- the canonical zero-driver recovery interface did not exist;
- an available nonfinite predictive residual was rejected as
  `available predictive row requires a successful finite state`;
- live spec/source authority capture and exact source-receipt SHA binding did
  not exist;
- module-issued fixture roots, parsed Log payloads, reviewed retry transitions,
  captured `git write-tree` identity, and staged-tree publication binding did
  not exist;
- config post-create failure lacked the required immutable stop disposition;
- false spec/source config tuples passed freeze and pre-receipt validation;
- false spec/source config/preholdout/holdout tuples returned
  `CONTINUE_FROZEN_CANDIDATE` at the immediate-pre-RNG boundary.

No NumPy RNG was constructed. The pre-RNG counterexample used only a list
append spy.

## Direct Arrival Counterexample

A deterministic current-API probe supplied 12 complete development arrival
pairs plus 12 complete holdout pairs, with otherwise complete zero-driver and
equal-emission evidence. It exited `0` and returned:

```text
{'zero_attempted': 24, 'zero_evaluable': 24, 'arrival_attempted': 24,
 'arrival_evaluable': 24, 'arrival_wins': 24,
 'bootstrap_converged_count': 199, 'bootstrap_failed_count': 0}
```

This reproduces acceptance of development evidence as the 24-pair holdout
denominator.

## Runbook Counterexample

Parsing all 18 executable `bash` fences found the sentence beginning
`Immediately before freeze-tracked-state` inside block 13. The assertion that
no executable block contains this prose failed with exit `1`.

No Task 3 command, production RNG construction, simulation, benchmark,
calibration, canonical config/artifact/receipt production, production freeze,
holdout, staging, commit, push, reset, restore, cleanup, or repository-file
deletion occurred during RED capture. Temporary-directory serializers and
exclusive-write guards were exercised; the false-authority pre-receipt
counterexample created only its temporary receipt, which is the defect RED was
intended to reproduce.
