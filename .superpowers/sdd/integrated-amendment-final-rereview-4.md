# Goal 023 Integrated Amendment Final Rereview 4

Date: `2026-07-12`
Profile: `sol_max_auditor`
Mode: fresh independent adversarial rereview, read-only except this ignored report

## Claim Audited

This review asks whether the exact supplied Goal 023 authority and pre-simulation
implementation are complete and fail-closed enough to begin Task 3 fixture-only
implementation. Operational authorization requires the frozen scientific truth,
schemas, evidence frames, recommendation inputs, source identities, and later
repository-state transitions to be independently reconstructable, and requires
invalid or contradictory evidence to fail before it can support a scientific
gate, retry, publication transition, or terminal acceptance.

The prior rereview and repair reports were treated as leads, not proof. The
current Goal, Plan, Runbook, authoritative spec, source receipt, source, tests,
complete Log, amendment proposal, rereview 3, and repair 3 report were read
against live disk and Git state.

## Binary Verdict

**NOT SUPPORTED. Task 3 is NOT AUTHORIZED.**

No new Critical finding was established, but five Important findings remain.
Task 3 fixture implementation, Goal 023 RNG/vector construction, simulation,
runtime benchmarking, calibration, canonical config/artifact/receipt production,
freeze, holdout, staging, commit, push, and publication remain **BLOCKED**.

The repaired C1 live-authority path, natural-support checks, holdout-only arrival
frame, predictive nonfinite state, authoritative spatial frames, fixture
destination isolation, Runbook syntax, authority tuple, Goal/spec body identity,
Log parent chain, empty index, and no-exposure state are supported. They do not
overcome the counterexamples below.

| ID | Severity | Result |
| --- | --- | --- |
| I1 | Important | Recovery truth and fit-derived science values are not bound to frozen generating truth or fit evidence; a forged dense `beta_driver` truth passes the recovery gate components. |
| I2 | Important | The 98-name manifest is exact and green, but multiple tests assert less than their proposal-assigned behavior. |
| I3 | Important | External schema/config authority is still not self-contained or fully literal; distinct canonical config schema versions are accepted. |
| I4 | Important | Retry authorization uses a substring denylist and authorizes an opaque mutating command as non-generative. |
| I5 | Important | Publication and terminal-attestation mechanics do not implement the real two-checkout Runbook or exact-once terminal state. |

## Findings

### Important I1: Scientific recovery evidence remains caller-authoritative

The Goal freezes dense `beta_driver` truth at `1.25` (Goal lines 98-106) and
states that recovery truth is nullable only for a truth-free stress or an
unavailable fit/profile (Goal lines 1823-1860). The implementation does not
bind that truth to scenario/parameter authority:

1. `validate_replicate_recovery_row()` validates algebra against whichever
   `truth_value` the caller supplies, but never checks the frozen truth map
   (`source:6873-6994`). It also accepts null truth for a successful zero-driver
   control row.
2. `validate_primary_science_foreign_keys()` verifies only key existence and
   parameter membership; it does not cross-bind recovery estimate, fit status,
   likelihood, profile state, or generating truth to the referenced fit row
   (`source:6346-6396`).
3. `summarize_attempted_recovery()` consumes partial mappings directly and does
   not invoke the literal row validator or reject nonfinite/negative widths and
   errors (`source:6744-6798`).

A deterministic in-memory probe built 48 schema-valid dense holdout
`beta_driver` rows and 48 complete successful fit rows. It substituted
`truth_value=0.0` for the frozen `1.25`, then ran all currently exposed row,
complete-fit, foreign-key, and summary validators:

```text
forged_dense_beta_truth=0.0 frozen_truth=1.25
validated_rows=48
coverage_count=48
converged_count=48
median_absolute_error=0.0
median_interval_width=1.0
recovery_gate_components_pass=True
```

The same validator accepted 24 successful zero-driver recovery rows with null
truth, null errors, and null `truth_in_interval`; the control reconciler still
returned `zero_decision=pass`, `zero_evaluable=24`. A separate direct summary
probe accepted `interval_width=-1.0` and propagated nonfinite maximum width and
error values.

This can turn a scientifically false truth/evaluation frame into passing dense
recovery evidence. The frozen truth and fit execution table must be observed
inputs, not caller declarations.

### Important I2: Exact node inventory does not equal exact behavior coverage

AST/proposal checks prove exactly 98 unique required names, 98 manifest entries
in the same order, 98 unique top-level definitions, and no missing or duplicate
definition. The exact node command passed:

```text
98 passed in 0.79s
```

Inspection of the assertions shows that several nodes are materially weaker
than the required RED behavior in proposal section 11. Examples are sufficient
to falsify complete 98-behavior coverage:

- T3L-010 is assigned dense, structured, sparse, and irregular fixtures
  (`proposal:1662`). Its test uses three one-hot rows and asserts only the
  observed Brier mean (`tests:4562-4580`); it does not exercise any assigned
  schedule/frame class or the interval, median, expected-value, and error
  outputs.
- T3D-001 and T3D-004 are assigned exact even-median positions and full-width
  imputation (`proposal:1678-1682`). Their fixtures leave both central order
  statistics equal and never prove the 24th/25th or 12th/13th averaging rule
  (`tests:4821-4855`). The public summarizer also accepts impossible values, as
  shown under I1.
- T3R-008 is assigned exact rank-4 versus rank-2 vectors. It tests only local
  scenario strings and never invokes the global reducer (`tests:5244-5256`).
  T3R-010 represents six fixed equal-emission status rows with one caller
  boolean, `equal_status_exact`, rather than validating those rows.
- T3P-017 uses one `tmp_path` as the staging, commit, merge, and push root
  (`tests:6478-6568`), so it cannot test the Runbook's worktree-to-canonical-
  checkout transition.
- T3P-022 retries the old `before` object and old payload
  (`tests:6654-6715`). It never tries a newly parented second attestation, the
  exact recursive case its assigned behavior says must fail (`proposal:1758`).

Other nodes similarly use implementation-owned constants on both sides of an
assertion, caller booleans in place of emitted evidence, or local helper results
in place of the assigned global rank. The green run is useful regression
evidence, but it is not evidence for all 98 literal scientific behaviors.

### Important I3: Artifact schemas and config literals remain under-specified

The repair added valuable full schemas for the model parameter and six
fit-derived tables. The complete external authority still contains unresolved
placeholders and implementation-selected values:

- `scenario_definitions.csv` calls `scenario_role`, `generation_model`,
  `fit_model`, `schedule_id`, `expected_behavior`, `truth_access_class`, and
  `transportability_class` enums but never enumerates their domains
  (Goal lines 1650-1681). The later shared enum block does not define them
  (Goal lines 1764-1790).
- `control_decision_summary.csv` calls `gate_family` an enum, but no literal
  domain is present; verification check names are then defined by those
  unresolved values (Goal lines 2051-2128 and 2369-2372).
- JSON schemas list types for `schema_version` and many nested strings without
  freezing their literal values. Config model, estimator, scenario, gate,
  boundary-label, and schema-version bytes are therefore selected partly by
  source constants rather than a self-contained external authority
  (Goal lines 2280-2360).
- There is no complete row validator for every authoritative CSV, notably the
  predictive summary, coverage summary, model-parameter, scenario-definition,
  profile, and control-decision artifacts. Several reducer inputs remain
  booleans rather than parsed emitted rows.

The implementation confirms the ambiguity. `_validate_config_schema()` accepts
any nonempty `schema_version` (`source:7812-7816`). An in-memory probe changed
only that field and both canonical documents validated:

```text
accepted_config_schema_versions=[('v1', 13143), ('anything-nonempty', 13158)]
```

Those byte-distinct configs produce different self/file identities while both
claiming canonical validity. Task 3 cannot implement one reproducible external
contract while multiple undeclared serializations remain valid.

### Important I4: Retry classification is not fail-closed

Current-envelope and reviewed Log-only transition binding are genuine repairs.
The remaining command-class check is a substring denylist for `holdout`,
`artifact`, `calibration`, and `benchmark`, plus four phase names
(`source:8302-8348`). It does not prove that an otherwise opaque command is a
non-generative validation command.

A deterministic authorization probe did not execute the command. It created a
valid nonzero failure, exact reviewed Log transition, and fresh current
envelope, then supplied:

```text
('python', '-c', "open('/tmp/forbidden-output','w').write('x')")
```

Observed:

```text
opaque_mutating_command_retry_authorized=
  ('python', '-c', "open('/tmp/forbidden-output','w').write('x')")
```

`validate_task6_command()` uses the same open-ended pattern
(`source:8939-8945`). Detecting mutation after such a command is too late for
immutable artifacts and receipts. Retry and post-holdout dispatch need a closed
typed allowlist of exact non-generative commands, not lexical inference.

### Important I5: Publication and terminal state fail under live semantics

#### Two-checkout publication identity

Runbook section 9 commits in the Goal 023 worktree, then changes directory to
`/Users/bwbrook/papers/spatext` for merge and push (Runbook lines 529-552).
`validate_publication_transition()` instead requires every captured publication
state's resolved checkout root to equal the staging worktree root
(`source:8823-8844`). T3P-017 hides the mismatch by using one root for all
states.

A deterministic fake-Git probe used otherwise valid object IDs and the two
distinct roots prescribed by the Runbook:

```text
runbook_two_checkout_merge_accepted=False
error=ValueError: publication transition requires captured live Git object state
```

The identity should be the shared Git repository/common object store plus the
validated tree, not equality of worktree directories.

#### Terminal attestation

`apply_terminal_attestation()` has three independent defects
(`source:8976-9006`):

1. It does not bind `log_path` to the canonical Goal 023 Log under the captured
   repository.
2. It rejects a realistic `git add Log.md` capture because staging changes
   `cached_entries` as well as `staged` and `log_bytes`, yet the function permits
   exactly the latter two fields.
3. Its exact-once check asks only whether the current parent ends with the new
   payload. A second payload generated from the first post-attestation envelope
   is different and is accepted.

A cleaned deterministic `/tmp` probe observed:

```text
arbitrary_log_path_first_attestation_accepted=True
recursive_second_attestation_accepted=True
realistic_cached_blob_change_outcome=
  ValueError: terminal attestation changed data outside the observed Log/index state
realistic_log_was_appended_before_rejection=True
```

Thus the implementation permits recursive acceptance on an arbitrary file and
can mutate the real Log before rejecting the normal index transition. This is
not exact-once terminal state.

## Repaired Surfaces Supported

The following rereview-3 repairs survived current inspection and bounded
counterexamples:

- Live spec and accepted source-receipt identities are reconstructed at config,
  freeze, pre-receipt, post-receipt, and immediate-pre-RNG boundaries. False
  spec/source tuples fail before creation or before the RNG spy.
- Successful fit rows enforce all five natural supports, strict ordered rates,
  exact boundary labels, and an interior equal-rate MLE.
- Control reconciliation requires exactly 24 zero-driver holdout rows, 24
  same-source arrival holdout pairs on the fixed 4,180/1,045 frames, and 199
  complete equal-emission bootstrap pairs.
- The available nonfinite predictive residual state is representable as null
  residual plus true nonfinite flag, with mandatory warning binding.
- Independent source reconstruction reproduced the accepted landscape and
  arrival hashes and all headline counts.
- Independent spatial reconstruction reproduced 5,225 passable cells, the
  1,306-cell sparse frame, and disjoint 4,180/1,045 fit/score frames with union
  5,225.
- Fixture emission requires a module-issued new system-temporary root and
  rejects the canonical artifact directory and resolved aliases before write.
- All 18 executable Runbook bash fences pass `bash -n`.

## Authority And Structural Evidence

The exact supplied tuple reproduces:

| Object | SHA-256 / size |
| --- | --- |
| Goal | `c20981e0062a03453f99f066cce460e0bcbb2717b803ee009b7e36eb2a9c6af6` |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook | `ffae51c58789fd721032ce734c0ef0250bc2a2727bfbc99530ecd2f16dd20804` |
| authoritative spec | `ccd3f601224f36782d44ee43e325214e8ba66928b8e97fc531fe41419341c7d2` |
| source | `f18ea913632b07de9f5108bdd23e5ef2a799d20b1a710c6ce5418776e1441e1a` |
| tests | `37dee62067c03b8a5e4b47430c1b347f160d5c2580c966644abba66d4cdf2575` |
| Log | `0bbd23f592a57c875e9b12a109c06cedf5912f8eb8697e14ba156bc50966d030`; 2,784 lines; 138,517 bytes |
| source receipt | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |

Goal and spec bodies from `## Objective` are byte-identical: `117226` bytes,
SHA-256
`416890f17cd4ac3ab785dad190b165b05b7a76ae8425e7ab1f51277feccb4282`.

Independent source reconstruction, using in-memory canonical CSV only:

```text
landscape_sha256=53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a
arrival_sha256=5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba
source_sha256=6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0
counts=(6048 landscape, 5225 passable, 823 water,
        4605 colonised by 120, 4289 finite prey extirpations)
```

The complete Log was parsed. All `16/16` parent hashes and `7/7` declared
parent byte counts reproduce. The historical legacy break remains explicitly
quarantined; the current root and all later children are intact.

## Bounded Validation

Fresh exact manifest command:

```bash
uv run python -c 'import runpy,pytest; p="tests/test_synth_medium_latent_response_observation_recovery.py"; n=runpy.run_path(p)["AMENDMENT_TEST_NAMES"]; raise SystemExit(pytest.main([*(f"{p}::{x}" for x in n), "--no-cov", "-q"]))'
```

Observed: `98 passed in 0.79s`, exit `0`.

Static and structural checks:

```text
proposal/AST/manifest: required=98, required_unique=98,
                       manifest=98, manifest_unique=98,
                       manifest_matches=true, missing=[], duplicate_defs=[]
Ruff format check:     2 files already formatted
Ruff check:            All checks passed!
mypy --no-incremental: Success: no issues found in 59 source files
git diff --check:      pass
owned untracked check: 8 files, no whitespace diagnostics
Runbook bash parse:    18 blocks, 0 failures
Goal/spec body hash:   identical
Log chain:             16/16 hashes, 7/7 byte counts
```

The full 297-test Goal file and production workflows were not run. The requested
exact 98-node manifest and bounded checks were run, and deterministic direct
counterexamples resolve the authorization claim without Task 3 or stochastic
execution.

## Repository And Exposure State

```text
branch: codex/spatext-goal023-latent-response-observation-gate
HEAD:   53462d0365babf2c8070714a930f69b4071af276
base:   origin/main = 53462d0365babf2c8070714a930f69b4071af276
index:  empty
remote Goal 023 branch: absent by live git ls-remote
```

The canonical artifact directory, recovery config, preholdout receipt, holdout
receipt, and production Goal 023 CLI are absent. The pre-review tracked and
untracked footprint is unchanged. No Task 3 command, Goal 023 RNG object or
payload, production stochastic vector, simulation, runtime benchmark,
calibration, canonical artifact/config/receipt, freeze, holdout, staging,
commit, push, publication, reset, restore, or cleanup was run.

The exact manifest used deterministic arrays, fake runners, list-append spies,
and temporary serializers only. Additional counterexamples were in memory or
under cleaned `/tmp` paths and never executed the opaque command shown above.

## Complete Correction Sequence

1. Keep Task 3 and every stochastic or irreversible phase blocked. Append no
   acceptance record to `Log.md`.
2. Freeze a literal scenario/parameter truth-authority map. Require every
   recovery row's truth value and nullability to equal that map; only the
   explicitly truth-free continuous-abundance rows may omit truth when the fit
   is otherwise available.
3. Replace key-only fit/science reconciliation with table-specific parsed row
   reconciliation. Cross-bind fit status, variant, estimate, log likelihood,
   boundary/profile state, and permitted parameter subset to exactly one fit
   row. Recompute recovery errors, interval membership, coverage, and summaries
   from those bound rows.
4. Make every summary consume only complete validated rows. Reject nonfinite or
   negative widths/errors, impossible intervals, out-of-support values,
   contradictory profile states, wrong split counts, and caller-supplied
   coverage/event booleans.
5. Complete external authority for all 22 artifacts: literal schema versions,
   every enum domain (including scenario and `gate_family` domains), full row-
   specific nullability, keys/sorts, JSON nested keys and literal strings,
   receipt namespace/version values, report links, and visual source tables.
   Make the source constants a transcription of that authority, not the only
   place the values exist.
6. Audit all 98 proposal rows against their test ASTs and assertions. Strengthen
   each under-covered existing node without changing the 98 names or order.
   At minimum cover the literal fit header/status rows, four T3L-010 fixture
   classes and every metric, exact even-median central values, global rank
   transitions, six equal-emission statuses, independent hash calculations,
   all immutable envelope fields, real two-worktree publication, and recursive
   terminal rejection.
7. Replace retry and Task 6 substring screening with a closed typed registry of
   exact Runbook section 7 non-generative validation commands. Bind the command
   class, argv, phase, and reviewed transient disposition in the failure and
   retry records. Reject every unregistered command before execution.
8. Bind staging/publication identity to the shared Git repository/common object
   store and validated `git write-tree`, while retaining each checkout's exact
   path and branch. Add a real temporary Git repository with two worktrees and
   prove commit, fast-forward merge, and push-state transitions end to end.
9. Redesign terminal attestation around the exact canonical Log path and a
   durable terminal record type. Reject any second terminal record even when it
   has a new parent. Model the real `git add Log.md` changes to cached/index and
   status fields, preserve every non-Log blob, and return an explicit immutable
   stop if any post-append observation fails.
10. Capture behavior-specific RED for every correction, implement to GREEN,
    then rerun the exact 98-node manifest, all bounded static checks, complete
    non-generative Goal 023/upstream regressions, source/frame reconstruction,
    all Runbook bash parses, authority hashes, Log-chain verifier, empty-index
    check, no-exposure checks, and a real two-worktree provenance integration
    test.
11. Append at most one new parent-bound repair child after all checks pass. Keep
    scientific, statistical, executor, artifact/schema, code, provenance, and
    max-review dispositions `PENDING`, then obtain a fresh independent max-tier
    rereview of the new exact source/test/Log tuple.

## Residual Uncertainty

The accepted Task 1/2 likelihood and spatial-source work was not falsified.
There is still no holdout or production exposure. The unresolved risk is the
pre-simulation evidence/provenance contract: wrong truth can support apparent
recovery, the green node matrix overstates behavioral proof, canonical artifact
bytes are not uniquely specified, and later retry/publication/terminal paths do
not enforce their declared state machine.

## Stop Rule

The binary gate is failed. The next legitimate action is bounded RED-GREEN
contract repair and another hash-specific independent rereview, not Task 3.
