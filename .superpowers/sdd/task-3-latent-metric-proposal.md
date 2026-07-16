# Goal 023 Task 3 Latent-Transition Metric Proposal

status: `PROPOSAL_ONLY_BARRY_DECISION_REQUIRED`
date: `2026-07-11`
worktree: `/Users/bwbrook/.codex/worktrees/spatext/goal023`
branch: `codex/spatext-goal023-latent-response-observation-gate`
HEAD/base: `53462d0365babf2c8070714a930f69b4071af276`

## Decision Summary

Adopt an ordered 21-category finite-horizon transition outcome:

```text
event at 6, 12, ..., 120, or administratively censored after 120.
```

Score that outcome with:

1. cumulative-incidence Brier score over all 20 event endpoints;
2. a positively scaled proper 90% central interval score on the same ordered
   support; and
3. absolute error of the posterior median, aggregated as the median across
   evaluation cells.

The first two are proper probabilistic scores. The third is an interpretable
resolution diagnostic and must not be described as a full-distribution proper
score.

The proposal includes deterministic grid-derived thresholds. It does not use a
development, calibration, or holdout scenario result to choose them. No
scenario, fit, profile, predictive ensemble, RNG payload, calibration, or
holdout payload was run for this proposal.

This is a material controlled-contract choice. It closes a Critical Task 3
authority gap, changes what counts as latent-response recovery in three nested
scenarios, and fixes the scientific cost assigned to administrative censoring.
Barry should approve or reject it before Goal/spec/Plan/Runbook are amended or
Task 3 RED tests are written.

## Authority And Interface Basis

The proposal is based on the accepted authority tuple:

```text
Goal     cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20
Plan     df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e
Runbook  78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed
spec     0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d
```

Accepted Task 2a provides:

- event paths at endpoint times `6,12,...,120` plus one censor path;
- post-transition endpoint emissions and a present `t0` state;
- immutable evaluator truth with finite transition endpoint or censoring;
- normalized scalar analyst path weights with shape `(21,)`; and
- deterministic cell IDs, schedules, frames, and analyst/truth separation.

The current Task 2b work additionally exposes a batched analyst path-weight
surface with shape `(n_cells, 21)`. Its live source/test hashes are
`eef58af9aa809bd7d0c055a368a3eb2f2975b4056043420edbd571a82fe93b92`
and
`10c0f460bd26088a85d3edd56752cf5f592cc716d3e9835e48ce1779325008bb`,
respectively. Task 2b is still pending independent acceptance, so Task 3 must
bind to its future accepted hashes rather than treating these live hashes as an
accepted handoff.

## Alternatives Considered

### Recommended: ordered cumulative and quantile scores

Use the cumulative Brier score, central interval score, and posterior-median
absolute error defined below. This respects the ordering of transition times,
retains censoring in every denominator, and maps exactly onto the accepted
21-path interface.

### Rejected: ordinary 21-class Brier score

The ordinary multiclass Brier score is proper, but it assigns the same
off-diagonal geometry to an event at `6` predicted as `12` and an event at `6`
predicted as censoring. It therefore discards the scientific ordering that the
6-unit time grid was designed to represent.

### Rejected: event-only errors or IPCW survival scores

Dropping censored cells would make apparent accuracy depend on the event
fraction and would permit denominator shrinkage. IPCW is unnecessary here:
the synthetic evaluator knows exactly whether each cell transitioned by `120`.
Administrative censoring is a modeled terminal outcome, not unknown
loss-to-follow-up. Observation dropout removes emission factors, not evaluator
transition truth.

## Ordered Outcome Contract

Index the 21 paths by `r = 1,...,21` and define their ordered evaluation values

```text
v_r = 6 * r.
```

Thus `v_1,...,v_20 = 6,...,120`. `v_21 = 126` is a label for the category
`T > 120`; it is not a claim that a censored transition occurred at time 126.
It places administrative censoring one canonical grid slot after an event at
`120`, which is the smallest ordering extension compatible with the frozen
6-unit grid.

For cell `x`, evaluator truth is

```text
R_x = transition_time / 6       for transition_time in {6,...,120}
R_x = 21                        for right censoring after 120
U_x = v_(R_x).
```

Let the analyst-side path vector be

```text
p_xr = P(T_x = v_r | analyst history, fitted plug-in parameters), r <= 20
p_x,21 = P(T_x > 120 | analyst history, fitted plug-in parameters).
```

These are latent-path conditional weights at a plug-in fit. They are not a
parameter-posterior sample and must not be reported as an MCMC or full
Bayesian posterior.

### Process-oracle adapter

For `process_oracle_observed_transition`, construct the 21 probabilities from
`transition_log_path_masses` at the fitted process-oracle parameter estimate
and each cell's analyst-visible `Q_x` and `TP(x)`. Do not condition these
probabilities on the cell's supplied oracle transition outcome. The oracle
transition is passed separately to the evaluator only after the probability
matrix is complete. This makes the metric a process-distribution calibration
check rather than the tautological score of a one-hot truth vector.

### Joint adapter

For ordinary joint fits, use the normalized output of
`batched_joint_path_posterior_weights` at the fitted MLE. The metric evaluator
accepts only ordered cell IDs and the frozen probability matrix. Truth enters a
separate evaluator-only argument and cannot enter starts, bounds, objectives,
profiles, plug-in weights, sorting, or fit classification.

## Input Validation And Firewall

Before scoring, require all of the following:

- exact expected sorted integer cell IDs on both analyst and evaluator sides;
- exact one-to-one ID equality, with no inner join or row dropping;
- a `float64` probability matrix of exact shape `(N, 21)`;
- finite entries with every entry at least zero;
- each row sum within `1e-12` of one;
- finite transition truth exactly on `6,12,...,120`, or the accepted censor
  sentinel in evaluator storage; and
- a successful finite applicable fit and every prerequisite design gate.

For a row sum within tolerance, divide by its finite positive sum once in
`float64`; do not clip entries or discard censor mass. A negative entry, a sum
outside tolerance, a missing/extra/duplicate cell, an invalid truth time, or a
nonfinite score fails the complete replicate metric. It never removes a cell
from a denominator.

The metric kernel must be pure and deterministic. Tests must show that changing
evaluator truth changes only the score and cannot alter any fitted parameter or
analyst path probability.

## Evaluation Frames And Denominators

`sample_size` is always the number of cells in the frozen evaluation frame,
not the number of finite events and not the number of retained count
opportunities. The Brier score has an internal fixed denominator of
`20 * sample_size`; the CSV still records the cell count as `sample_size`.

| Scenario | Latent metric status | Evaluation frame | `sample_size` |
| --- | --- | --- | ---: |
| `process_oracle_observed_transition` | applicable | all passable cells | `5225` |
| `observation_oracle_fixed_transition` | not applicable | none | `0` |
| `dense_count_exact_model` | applicable gate | all passable cells | `5225` |
| `structured_imperfect_effort` | applicable gate | all passable cells | `5225` |
| `sparse_expected_failure` | applicable diagnostic | frozen sparse frame | `1306` |
| `zero_driver_effect_negative_control` | applicable diagnostic | all passable cells | `5225` |
| `permuted_arrival_alignment_stress` | applicable diagnostic | frozen score frame, primary permuted fit only | `1045` |
| `no_emission_contrast_negative_control` | not applicable | none | `0` |
| `informative_dropout_misspecification_stress` | applicable diagnostic | all passable cells | `5225` |
| `goal018_continuous_abundance_stress` | not applicable | none | `0` |
| `spatial_frailty_stress` | applicable diagnostic | all passable cells | `5225` |

Observation-oracle latent scores would be a tautology because true transitions
are fixed in that likelihood; its inferential target is the two emission rates.
Equal-emission fitting does not identify an analyst latent-path distribution.
The Goal 018 continuous-abundance stress has no Goal 023 binary transition
truth. Those scenarios therefore emit explicit `not_applicable` rows rather
than zero scores.

For each scientifically scheduled scenario/split/replicate, emit exactly three
rows in metric order, including explicit not-applicable rows. Do not emit rows
for a split that the scenario contract does not instantiate. Not-applicable
rows use `sample_size=0`, nullable score fields empty, and
`gate_result=not_applicable`.

All administratively censored cells remain in `N`. For informative dropout,
all 5,225 cells remain even if a cell loses every count opportunity; such a
cell receives an empty analyst history and its path probabilities reduce to
the fitted process distribution. The current observation helper's omission of
cells with no retained opportunities must not be allowed to shrink this Task 3
evaluation frame.

## Exact Metric Definitions

### `transition_brier`

For endpoint `j = 1,...,20`, define

```text
F_xj = sum(p_xr for r <= j)
I_xj = 1 if R_x <= j else 0.
```

The observed value is the cumulative-incidence integrated Brier score

```text
observed_value = sum_x sum_j (F_xj - I_xj)^2 / (20 * N).
```

The exact analyst-distribution expected value is

```text
expected_value = sum_x sum_j F_xj * (1 - F_xj) / (20 * N).
error = observed_value - expected_value.
```

The score lies in `[0,1]`. It is strictly proper for the complete ordered
21-category distribution because all 20 cumulative probabilities uniquely
determine all 21 path masses. A censored truth has `I_xj=0` at every endpoint;
its probability mass is therefore scored without dropping or imputing the
cell.

### `transition_interval_score`

Fix `alpha_interval = 0.10`. For any `q in (0,1)`, use the deterministic lower
discrete quantile

```text
Q_x(q) = min(v_r such that sum(p_xs for s <= r) >= q).
```

Set `L_x = Q_x(0.05)` and `H_x = Q_x(0.95)`. Define the positively scaled
central interval score

```text
S_x(u) = 0.05 * (H_x - L_x)
         + (L_x - u) * 1(u < L_x)
         + (u - H_x) * 1(u > H_x).
```

This is exactly `alpha_interval / 2` times the conventional interval score.
Positive scaling preserves propriety and leaves the score in time units. It
also makes a zero-width point forecast's score equal its absolute timing error.

```text
observed_value = sum_x S_x(U_x) / N
expected_value = sum_x sum_r p_xr * S_x(v_r) / N
error = observed_value - expected_value.
```

The score lies in `[0,120]`. It is proper for the 5th and 95th quantiles, but
not strictly proper for the complete path distribution; the Brier score carries
that role. The censor category participates in quantiles and tail penalties as
`v_21=126` without being interpreted as an actual event time.

### `transition_median_absolute_error`

Set the deterministic posterior median `M_x = Q_x(0.50)` and cell loss

```text
A_x = abs(U_x - M_x).
```

The observed value is the ordinary median of all `N` cell losses. For even
`N`, sort ascending and take the arithmetic mean of the two central values.
No cell is excluded.

For a deterministic posterior-resolution comparator, define

```text
B_x = sum_r p_xr * abs(v_r - M_x)
expected_value = ordinary_median(B_1,...,B_N)
error = observed_value - expected_value.
```

The observed and expected values lie in `[0,120]` time units. `M_x` minimizes
posterior expected absolute loss for each cell, but the cross-cell median
aggregation is descriptive and is not itself a strictly proper
full-distribution score. `error` is therefore a resolution contrast, not a
calibration residual with a claimed null distribution.

## Exact-Model Expectations

The definitions imply the following invariant expectations:

- a correct one-hot event or censor forecast has all three values and all three
  expected values equal to `0`;
- under calibrated nondegenerate path probabilities, the expectation of
  observed Brier equals its row's `expected_value`;
- under calibrated nondegenerate path probabilities, the expectation of the
  observed interval score equals its row's `expected_value`;
- a no-count history remains scoreable from its fitted process path masses;
- censoring probability is rewarded only when evaluator truth is censored and
  is penalized progressively as an observed event lies farther before the
  horizon; and
- the MAE expected field is the median of cellwise posterior Bayes risks, not
  the exact expectation of the sample median.

## Preregistered Thresholds

The thresholds are fixed from the accepted 6-unit outcome grid, not from
scenario performance.

For a one-hot forecast displaced by exactly one six-unit category:

```text
transition_brier = 1 / 20 = 0.05
transition_interval_score = 6
transition_median_absolute_error = 6.
```

Two categories correspond to the 12-unit structured schedule and four to the
24-unit sparse schedule. This gives the exact threshold scale:

| Resolution scale | Brier | Scaled interval score | Median absolute error |
| --- | ---: | ---: | ---: |
| one 6-unit category | `0.05` | `6` | `6` |
| one 12-unit structured interval | `0.10` | `12` | `12` |
| one 24-unit sparse interval | `0.20` | `24` | `24` |

All inequalities below are inclusive. A value equal to a threshold passes.

### Nested per-replicate rules

| Scenario | `transition_brier` | `transition_interval_score` | `transition_median_absolute_error` |
| --- | --- | --- | --- |
| process oracle | `error <= 0.05` | `error <= 6` | `error <= 6` |
| dense exact joint | `observed_value <= 0.05` | `observed_value <= 6` | `observed_value <= 6` |
| structured exact joint | `observed_value <= 0.10` | `observed_value <= 12` | `observed_value <= 12` |

The process oracle is judged against its own exact fitted-distribution expected
score because a correctly specified stochastic process is not expected to
predict every realized event time sharply without count information. Its
one-sided excess rule does not fail an unusually good realization. Dense and
structured joint fits make an explicit latent-time resolution claim, so they
receive absolute ceilings tied to their canonical observation spacing.

For development rows, a valid value within the corresponding rule is
`diagnostic`, an exceedance is `warning`, and an unavailable required fit is
`fail`. Development never changes a threshold.

For calibration and holdout, each valid applicable row is `pass` or `fail`
under the literal rule above. Aggregate each metric separately over every
attempted replicate:

| Scenario | Calibration minimum | Holdout minimum |
| --- | ---: | ---: |
| process oracle | `23/24` passing rows | `46/48` passing rows |
| dense exact joint | `23/24` passing rows | `46/48` passing rows |
| structured exact joint | `22/24` passing rows | `44/48` passing rows |

These reuse the already frozen `0.95/0.95/0.90` nested fit-availability rates;
they are scientific resolution tolerances, not binomial hypothesis tests. A
calibration failure stops before freeze. It does not authorize threshold,
schedule, support, estimand, seed, or model tuning. Every missing or failed row
remains in the attempted denominator as a failure.

### Sparse, controls, and stresses

These rows are diagnostic and cannot rescue or replace their existing scenario
gates.

| Scenario | Warning scale |
| --- | --- |
| sparse expected failure | raw value above `0.20 / 24 / 24` in metric order |
| zero-driver control | raw value above `0.05 / 6 / 6` |
| permuted-arrival stress | raw value above `0.10 / 12 / 12` |
| informative-dropout stress | raw value above `0.10 / 12 / 12` |
| spatial-frailty stress | raw value above `0.10 / 12 / 12` |

A valid value at or below its warning scale is `diagnostic`; a value above is
`warning`. Sparse performance better than its warning scale is not a failure:
the frozen sparse honesty claim remains its 24-attempt `beta_driver` coverage
and interval-width rule. A latent warning in a stress is additional evidence
only. It does not satisfy the already frozen count-predictive warning
requirement, alter the zero-driver false-signal test, or replace the
arrival-alignment heldout-score rule.

## Missingness And Failure Handling

Apply these rules in order:

1. A scenario with no scientifically meaningful latent-path target emits the
   three explicit not-applicable rows described above.
2. A nonconverged or nonfinite required fit emits three rows with the frozen
   frame `sample_size`, empty `observed_value`, `expected_value`, and `error`,
   and `gate_result=fail`.
3. A successful fit with a failed prerequisite potential, oracle-at-risk, or
   plug-in design gate emits the same three nullable failed rows as an
   unavailable fit. Do not compute or retain a latent score that could decorate
   or soften a failed design prerequisite.
4. A missing profile does not make path probabilities unavailable when the MLE
   itself is finite. The metric may be computed, while the separate profile or
   recovery gate still fails under its own contract.
5. Missing count opportunities remove emissions only. They never remove
   transition intervals, censor mass, cells, or truth from latent-metric
   denominators.
6. Any cell-level analyst/evaluator mismatch, invalid probability vector,
   invalid truth, or nonfinite metric fails all three replicate rows. There is
   no partial-cell score and no complete-case fallback.
7. CSV output uses empty fields only where the schema permits structural nulls;
   no NaN or infinity is serialized.

## Gate And Recommendation Integration

- Process-oracle latent-metric failure is a process-oracle failure and maps to
  `model_contract_failed`.
- Dense latent-metric failure after both oracle layers pass is dense joint
  recovery failure and maps to `process_observation_confounded`.
- Structured latent-metric failure after dense passes, while structured
  coverage remains calibrated and false positives remain controlled, is
  structured recovery/precision failure and maps to
  `observation_limited_but_calibrated`.
- `latent_response_observation_gate_passed` requires the process-oracle, dense,
  and structured latent metric families to pass. The observation-oracle latent
  family is explicitly not applicable and neither helps nor harms that gate.
- Sparse/control/stress latent rows remain diagnostic under their existing
  scenario-specific gates.

This proposal does not resolve the other Task 3 precedence gaps identified in
the scenario preflight. In particular, a structured required-fit or predictive
failure, as distinct from a finite latent-resolution failure, still needs the
separate total-precedence amendment before Task 3 implementation.

Aggregate calibration/holdout pass counts and thresholds should be recorded in
the existing scenario gate details in `verification.json` and the human report.
The frozen config should add a literal `latent_time_thresholds` object. Any
authority amendment must define that nested schema explicitly; Task 3 must not
hide these values as source constants.

## Required Deterministic Tests

Before implementation acceptance, RED tests should require:

1. exact event/censor index mapping and `v_21=126` label semantics;
2. one-hot correct event and censor vectors score exactly zero;
3. a one-category point displacement scores exactly `0.05`, `6`, and `6`;
4. event-at-6 versus censor point forecasts score exactly `1`, `120`, and
   `120`;
5. cumulative Brier equals a handwritten 21-category example and its expected
   value equals the exact `F*(1-F)` calculation;
6. discrete 5th, 50th, and 95th quantiles use the first cumulative crossing,
   including exact-boundary ties and censor endpoints;
7. interval expected value equals direct enumeration over all 21 paths;
8. odd and even cell-count medians use the literal ordering rule;
9. process-oracle probabilities are computed before and independently of
   oracle truth;
10. dense/structured/sparse batched weights score identically to stacked scalar
    weights on deterministic fixtures;
11. empty count histories retain the full process path and frozen cell
    denominator;
12. every censored truth remains in every metric denominator;
13. shuffled, missing, extra, duplicate, nonfinite, negative, or nonnormalized
    probability rows fail the complete replicate;
14. a failed fit emits three explicit nullable failed rows and cannot reduce an
    aggregate denominator;
15. observation-oracle, equal-emission, and continuous-abundance rows are
    exactly not applicable rather than zero;
16. warning and pass boundaries are inclusive at `0.05/0.10/0.20` and
    `6/12/24`, with just-above fixtures failing or warning as specified;
17. aggregate count boundaries pass at `23/24`, `46/48`, `22/24`, and `44/48`
    and fail one count below; and
18. evaluator truth cannot enter or alter fitting, path-weight generation,
    profile construction, or recommendation inputs other than the post-fit
    latent score.

Use injected deterministic probability arrays and truth fixtures. These tests
need no seed, RNG construction, scenario execution, calibration row, or holdout
payload.

## Barry Decision

Recommendation: approve the ordered 21-category contract, including the
minimal `126` censor label, the scaled interval score, and the grid-derived
threshold table as one controlled pre-simulation amendment.

This decision is sufficiently material to require Barry because it:

- fixes a previously unspecified scientific acceptance gate;
- assigns an explicit loss geometry to event-versus-censor errors;
- adds nested calibration and holdout pass-count requirements; and
- changes recommendation inputs for process-oracle, dense, and structured
  recovery.

Until approved and transcribed into the tracked authority tuple with fresh
hash-specific scientific, executor-readiness, and provenance/freeze review,
Task 3 remains blocked. No implementation should infer these choices from this
ignored proposal alone.
