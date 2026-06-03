# `synth-small` Predator-Truth Sensitivity and Readiness

## Purpose

This document specifies a small deterministic sensitivity and readiness package
for the `synth-small` predator-response truth benchmark.

Goal 001 established that the current predator-truth artifact is structurally
coherent. This next step asks a different question: whether the current default
parameterisation is a useful deterministic benchmark for the first noisy
observation layer, or whether modest predator-response tuning should happen
first.

This package is not inference, fitting, or ABC. It is a local deterministic
review sweep around the current default.

## Scope

In scope:

- run a small deterministic grid around the current predator defaults,
- include the current default as an explicitly labelled baseline candidate,
- compute repeatable readiness metrics for each candidate,
- rank candidates using documented criteria,
- produce CSV, JSON, and Markdown review artifacts,
- recommend whether the current default is ready for the observation layer.

Out of scope:

- changing the default generator parameters,
- adding noisy observations,
- fitting or parameter recovery,
- stochastic model variants,
- remote or HPC execution.

## Candidate Grid

The initial local sweep should vary three predator-response controls:

- `predation_scale`
- `half_saturation`
- `ramp_duration`

The default candidate is:

```text
predation_scale = 1.0
half_saturation = 6.0
ramp_duration = 8
```

The first grid should be small enough for the Mac Mini development box. A
3-by-3-by-3 grid is acceptable for `synth-small`:

```text
predation_scale in {0.75, 1.0, 1.25}
half_saturation in {4.0, 6.0, 8.0}
ramp_duration in {6, 8, 10}
```

This yields 27 deterministic candidates including the default.

## Metrics

For each candidate, the sensitivity run should compute:

- verification pass/fail,
- extirpated and surviving fractions,
- finite lag min, max, mean, and standard deviation,
- low- and high-initial-abundance extirpation rates,
- west- and east-band extirpated counts,
- final-abundance mean,
- whether numerical clipping occurred,
- readiness classification,
- readiness score,
- criteria-level pass/fail flags.

The west/east band comparison should use the first and last five columns of the
`25 x 25` grid, matching the current western-boundary arrival benchmark.

## Readiness Criteria

The initial readiness criteria are deliberately simple and auditable.

A candidate is classified as `observation_ready` when all of the following are
true:

- the deterministic run verifies,
- extirpated fraction lies in `[0.20, 0.80]`,
- finite lag standard deviation is at least `2.0`,
- low-initial-abundance extirpation rate is greater than high-initial-abundance
  extirpation rate,
- west-band extirpated count is greater than east-band extirpated count,
- no non-negative clipping was used.

A candidate is classified as `review` when it verifies and passes at least four
of the six readiness criteria.

A candidate is classified as `not_ready` when it fails verification or passes
fewer than four criteria.

These labels are not biological truth claims. They are deterministic benchmark
readiness labels for deciding whether to add the first observation layer.

## Ranking

Candidates should be ranked using a transparent score. The score should reward:

- passing verification,
- intermediate extirpation fraction, ideally near `0.40`,
- non-trivial lag variation,
- stronger low-density vulnerability than high-density vulnerability,
- stronger western than eastern extirpation under western arrival,
- no numerical clipping.

The exact formula can be practical rather than statistically formal, provided
it is documented in the implementation and emitted outputs.

The default candidate should be reported separately even if another candidate
ranks higher. The aim is to decide whether the current default is good enough,
not to silently replace it.

## Output Contract

The sensitivity command writes under:

```text
artifacts/synth_small_predator_truth_sensitivity/
```

Required outputs:

- `sweep_results.csv`
- `candidate_rankings.csv`
- `readiness.json`
- `decision_memo.md`

### `sweep_results.csv`

One row per candidate with parameters, metrics, criteria flags,
classification, and score.

### `candidate_rankings.csv`

Rows sorted from best to worst under the documented score.

### `readiness.json`

Machine-readable decision summary including:

- run metadata,
- readiness criteria,
- candidate count,
- default candidate label and classification,
- best candidate label and classification,
- recommendation.

### `decision_memo.md`

Human-readable memo for Barry that states:

- whether the current default appears observation-ready,
- which candidate ranks best,
- what the sweep shows about sensitivity near the default,
- what remains scientific judgement rather than an automated decision.

## Acceptance Criteria

This work package is complete when:

- the sensitivity spec exists,
- the local sweep command writes all required outputs,
- tests cover metric extraction, classification, and report rendering,
- the default candidate classification is present in `readiness.json`,
- the full repo quality lane passes.

## Next Use

After the sensitivity package is generated, the next goal should be either:

- approve the current deterministic default and add the first synthetic
  observation layer, or
- tune the deterministic benchmark deliberately before observations are added.
