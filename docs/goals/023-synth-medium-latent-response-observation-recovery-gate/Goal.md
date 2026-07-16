# Goal 023: Synth-Medium Latent-Response Observation Recovery Gate

## Objective

Build and audit the first likelihood-coherent latent-response and observation
model for `synth-medium`. Determine whether a deliberately small ecological
response model and its observation parameters can be separately recovered from
raw cell-time count histories before any full spread fitting or real-data work.

This is a scheduled-count synthetic benchmark. A pass does not establish that
the model is transportable to irregular presence-only records.

## Source Boundary

Goal 018 supplies only:

- the accepted Goal 017 landscape;
- passability, habitat quality, and cell identifiers; and
- the fixed predator-arrival surface `TP(x)` from
  `balanced_corridor_detour_v2`.

The source APIs are
`spatext.synth.medium.landscape.build_synth_medium_landscape` and
`spatext.synth.medium.spread_impact.build_synth_medium_spread_impact_review_pack`.

Required source reconciliation is:

- source commit: `53462d0365babf2c8070714a930f69b4071af276`;
- landscape cells: `6048`;
- passable cells: `5225`;
- water cells: `823`;
- final predator-colonised passable cells: `4605`; and
- finite Goal 018 prey quasi-extirpations: `4289`.

Goal 023 defines a new stochastic response truth. It does not replace or alter
Goal 018 artifacts. Goal 018 deterministic abundance/lag behavior is used only
as an explicitly out-of-model stress, with no parameter-recovery claim.

Goal 019-022 observations and reconstructed response times remain historical
diagnostics and must not be fitted.

## Frozen Model Contract

The equations and estimands below are fixed before implementation. Task 0 must
copy them into the authoritative spec, obtain independent scientific approval,
and record the spec SHA-256 in `Log.md` before simulation code or holdout seeds
are materialised.

### Domain and covariates

- Model times are `t = 0, 6, ..., 120`.
- `A_x = TP(x)` is fixed and known for colonised cells. For passable cells with
  nonfinite Goal 018 arrival, define `G_xt = 0` for the full horizon.
- `Q_x` is Goal 017 habitat quality standardised over all passable cells as
  `(quality - passable_mean) / passable_population_standard_deviation`, using
  population mean and population standard deviation with `ddof=0`.
- `G_xt = max((t - A_x) / 30, 0)` is scaled time since predator arrival.
- All model arrays are `float64`. Frailty standardisation also uses population
  mean and population standard deviation with `ddof=0` over passable cells.
- Cells are conditionally independent in the fitted exact model. A spatial
  frailty stress tests this assumption.

### Latent response process

Each passable cell starts present: `Z_x0 = 0`. State `Z_xt = 1` denotes
quasi-extirpated and is absorbing. For a cell still present at the start of an
interval, the transition hazard is

```text
h_xt = 1 - exp(-exp(alpha + beta_driver * G_xt + beta_quality * Q_x)).
```

The no-driver null is `beta_driver = 0`; this removes every dependence on
`TP(x)` while retaining background decline and habitat effects. Transition
times after `120` are right-censored.

The driver coefficient is a conditional association parameter in Goal 023,
not a causal intervention estimand.

### Observation process

For each retained opportunity with known effort `E_xt > 0`:

```text
Y_xt | Z_xt = 0 ~ Poisson(E_xt * lambda_present)
Y_xt | Z_xt = 1 ~ Poisson(E_xt * lambda_quasi)
```

with `lambda_present > lambda_quasi > 0`. These are effective count rates per
unit effort. They do not separately identify abundance and detectability.
`lambda_quasi` combines residual true records and false/background records;
those mechanisms are not separately estimable in this goal.

The joint likelihood must marginalise exact discrete transition time. A
derived detection flag may be `Y_xt > 0`; it must not create a second
likelihood.

### Parameters and generating truth

| Parameter | Role | Fitting support | Generating value |
| --- | --- | --- | --- |
| `alpha` | baseline cloglog hazard intercept | `[-10, -2]` | `-6.0` |
| `beta_driver` | scaled time-since-arrival effect | `[-3, 3]` | `1.25` |
| `beta_quality` | standardised quality effect | `[-2, 2]` | `-0.60` |
| `lambda_quasi` | quasi-extirpated effective count rate | `[0.01, 1]` | `0.15` |
| `lambda_present` | present effective count rate | `[0.25, 10]`, ordered above `lambda_quasi` | `4.0` |

Bounds are part of the frozen contract, not tuned on holdout results.

### Exact timing and likelihood factorisation

Write `t_j = 6j` for `j = 0, ..., 20`. For `j = 1, ..., 20`, `D_xj` denotes an
event in `(t_{j-1}, t_j]`, conditional on `Z_x,j-1 = 0`, and

```text
eta_xj = alpha + beta_driver * G_x,t_j + beta_quality * Q_x
h_xj = 1 - exp(-exp(eta_xj)).
```

Stable process primitives are mandatory:

```text
log_survival_xj = -exp(eta_xj)
log_hazard_xj = log(-expm1(-exp(eta_xj)))
hazard_xj = -expm1(-exp(eta_xj))  # only when a probability is required
```

Never derive log survival through `log(1 - h_xj)`. Analytic tests must cover
all parameter-support extremes and the actual canonical `Q_x` range.

The hazard uses `G` at endpoint `t_j`. The state recursion is

```text
Z_x0 = 0
Z_xj = max(Z_x,j-1, D_xj).
```

The `t_0` emission always uses `lambda_present`. An endpoint `t_j` emission is
post-transition and conditional on `Z_xj`. If `T_x = t_k`, its path mass is

```text
P(T_x = t_k) = prod_{j < k}(1 - h_xj) * h_xk.
```

Right censoring has mass

```text
P(T_x > 120) = prod_{j=1}^{20}(1 - h_xj),
```

and the censored path stays present through `t_20`. Omitted count
opportunities remove emission factors only; every intervening transition
interval remains in the process factorisation.

For an event at `t_k`, the process-oracle log likelihood is

```text
sum_{j < k} log_survival_xj + log_hazard_xk,
```

and for censoring it is `sum_{j=1}^{20} log_survival_xj`. With fixed true
transitions, the observation-oracle log likelihood is the sum, over retained
opportunities only, of the conditional Poisson log probabilities using the
post-transition `Z_xj` rule above.

For analyst-visible count histories, define each event path `k = 1, ..., 20`
as present before `t_k` and quasi-extirpated from `t_k` onward, with one
additional all-present censored path. The exact joint cell log likelihood is

```text
logsumexp(
  log_process_path_mass(k)
  + sum_{retained j} log Poisson(Y_xj; E_xj * lambda_{Z_xj(k)})
  for k in {1, ..., 20, censored}
).
```

The deployable joint likelihood must marginalise all 20 event paths plus
censoring with `scipy.special.logsumexp`, even when observations are absent or
irregular. A separately coded forward recursion must equal direct enumeration
on analytic one-, two-, and 20-interval tests. A derived `Y_xj > 0` flag is not
a second likelihood.

### Poisson law and computational domain

The statistical support remains the unbounded nonnegative integers
`Y_xj in N_0`. The Task 1 `1_000_000_000` count/mean guard is only a
conservative computational-domain limit. It is not truncation, censoring,
zero-mass assignment, or renormalisation of the Poisson law. Any guard
violation aborts as `numerical_domain_failure` and cannot produce a scientific
classification. Frozen efforts and rate supports must be verified to remain
well inside this domain.

### Ordered-rate coordinate transform

Optimisation coordinates are `p_frac, q_frac in [0, 1]` with

```text
lambda_present = 0.25 + 9.75 * p_frac
q_upper = min(1.0, lambda_present - 1e-9)
lambda_quasi = 0.01 + (q_upper - 0.01) * q_frac.
```

The `1e-9` gap is computational only and must be exposed in the frozen config.
Reported parameters and profile targets are in natural space. Every
conditional nuisance transform must preserve both natural supports and strict
rate ordering.

### Deterministic global starts

The optimisation-coordinate order is
`alpha,beta_driver,beta_quality,p_frac,q_frac`. Use positive Halton indices
`1, ..., 8` with bases `2,3,5,7,11`; each radical-inverse value `u` maps to
`0.05 + 0.90 * u` of that coordinate's box. This yields the frozen starts:

| Start | `alpha` | `beta_driver` | `beta_quality` | `p_frac` | `q_frac` |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `-6` | `-0.9` | `-1.08` | `0.178571428571` | `0.131818181818` |
| 2 | `-7.8` | `0.9` | `-0.36` | `0.307142857143` | `0.213636363636` |
| 3 | `-4.2` | `-2.1` | `0.36` | `0.435714285714` | `0.295454545455` |
| 4 | `-8.7` | `-0.3` | `1.08` | `0.564285714286` | `0.377272727273` |
| 5 | `-5.1` | `1.5` | `-1.656` | `0.692857142857` | `0.459090909091` |
| 6 | `-6.9` | `-1.5` | `-0.936` | `0.821428571429` | `0.540909090909` |
| 7 | `-3.3` | `0.3` | `-0.216` | `0.0683673469388` | `0.622727272727` |
| 8 | `-9.15` | `2.1` | `0.504` | `0.19693877551` | `0.704545454545` |

No generating truth or data enters this table. Oracle fits use the applicable
coordinate subset from the same eight rows.

### Optimizer and convergence

- Runtime dependency addition remains limited to `scipy>=1.17,<2`.
- Every global, inverse-audit, and profile nuisance optimisation uses this
  literal call, with the applicable objective, start, and bounds:

```python
scipy.optimize.minimize(
    objective,
    x0,
    method="L-BFGS-B",
    jac="3-point",
    bounds=bounds,
    options={
        "ftol": 1e-12,
        "gtol": 1e-6,
        "maxiter": 1000,
        "maxfun": 20000,
        "maxls": 50,
        "finite_diff_rel_step": 1e-5,
    },
)
```

- A start converges only when `result.success` is true, `status == 0`, the
  objective and parameters are finite, and all natural supports plus strict
  ordering hold. Invalid or nonfinite evaluation is a failed start and is
  never clipped into success.
- A replicate converges only when at least six of eight starts converge and
  the best two finite log likelihoods differ by no more than
  `1e-6 * (1 + abs(best_log_likelihood))`. Sort converged global starts by
  descending log likelihood, then start index ascending; apply the best-two
  rule to the first two rows in that order.

### Profile-likelihood intervals

Use natural-space 90% profile-likelihood intervals with likelihood-ratio
cutoff `2.705543454095404`. Fix the target parameter in natural space. The
global rate map remains unchanged for profiles of `alpha`, `beta_driver`, or
`beta_quality`. Conditional rate maps are literal:

```text
lambda_present fixed at p*:
  lambda_quasi = 0.01 + (min(1, p* - 1e-9) - 0.01) * q_frac

lambda_quasi fixed at q*:
  lambda_present = max(0.25, q* + 1e-9)
                   + (10 - max(0.25, q* + 1e-9)) * p_frac.
```

Reject an invalid fixed value or support/order map. Natural-to-coordinate
projection clips only roundoff within `1e-12` of a coordinate box; farther
values are invalid. Deduplicate starts when maximum coordinate difference is
at most `1e-10`, retaining the first in frozen order.

For side index `m = 0, 1, ...`, the profile-point distance from the MLE is

```text
min(distance_to_bound, 0.02 * natural_support_width * 1.6^m).
```

Evaluate each unique natural-space point once. At each point, deduplicated
nuisance starts are attempted in this order: global MLE projection, nearest
already-successful point on the same side, then projected frozen global starts,
with at most eight attempts after deduplication. Select the best successful
profile optimum by descending log likelihood, then start-source order. If none
succeeds, the point fails and that side remains open.

The root function is

```text
2 * (LLmax - LLprofile) - 2.705543454095404.
```

Solve a sign-changing bracket with `scipy.optimize.brentq`,
`xtol = 1e-5 * natural_parameter_support_width`, and `maxiter=100`. Brent
evaluations use the same start order, with the nearest successful bracket or
profile optimum as the adjacent start. Tie selection is descending log
likelihood, then start-source order. A support bound closes an interval only
when it belongs to a sign-changing bracket; no sign-changing bracket at the
bound means the side is open and unidentified, never replaced by the bound.
If any successful profile log likelihood exceeds `LLmax` by more than
`1e-6 * (1 + abs(LLmax))`, the global fit is invalid and classification stops.

A practically identifiable parameter has a finite two-sided profile interval,
an MLE farther than 1% of support width from either bound, and a profile that
crosses the cutoff on both sides.

### Structural-identifiability proposition and audits

The following is a constructive sufficient-condition proposition, not an
unqualified identifiability claim. Known-present `t_0` emissions identify
`lambda_present`. Distinct ordered Poisson emissions plus supported follow-up
observations identify `lambda_quasi` and the observed-time survival-mixture
weights. Writing

```text
S_xj = exp(-sum_{k <= j} exp(eta_xk)),
```

dense successive survival differences identify interval hazards. Full column
rank of `[1,G,Q]` over the applicable dense interval design then identifies
`alpha`, `beta_driver`, and `beta_quality`.

Coarse 12- or 24-unit schedules identify block cumulative hazards directly,
not each six-unit interval hazard. Row rank alone is therefore insufficient;
joint identifiability for structured and sparse schedules is conditional on
injectivity of the parameter-to-observable-summary map.

Before estimation, run a deterministic numerical noncollision audit for each
canonical dense, structured, and sparse schedule at exactly these interior
natural parameter vectors, ordered as
`alpha,beta_driver,beta_quality,lambda_quasi,lambda_present`:

```text
A = (-6.0,  1.25, -0.60, 0.15, 4.00)
B = (-5.0,  0.50,  0.50, 0.30, 2.50)
C = (-7.0, -0.50, -1.00, 0.60, 6.00)
```

For each analyst-visible scheduled opportunity, sorted by integer `cell_id`
then ascending time, compute

```text
S_x0 = 1
S_xj = exp(-sum_{k <= j} exp(eta_xk))
mu_xj = E_xj * (lambda_present * S_xj + lambda_quasi * (1 - S_xj))
p0_xj = S_xj * exp(-E_xj * lambda_present)
         + (1 - S_xj) * exp(-E_xj * lambda_quasi).
```

Compute in `float64` and stable log space. The audit vector is all
`log1p(mu_xj)` values in canonical opportunity order followed by all
`log(p0_xj)` values in the same order. Use central differences with step
`1e-5 * natural_support_width`, then scale each Jacobian column by its natural
support width.

The SVD convention for any matrix is literal:

```text
n_rows, n_columns = scaled_matrix.shape
s = numpy.linalg.svd(scaled_matrix, compute_uv=False)
tol = max(n_rows, n_columns) * numpy.finfo(numpy.float64).eps * s_max
rank = count(s > tol)
condition = s_max / s_min if rank == n_columns else infinity.
```

For the canonical numerical noncollision audit, `scaled_matrix` is the scaled
Jacobian, `n_columns = 5`, and rank `5` with condition number below `1e8` is
required. The inverse objective is RMSE between candidate and target audit
vectors. Use exactly 16 starts: positive Halton indices `1, ..., 16`, bases
`2,3,5,7,11`, mapped as `0.05 + 0.90 * u` in the optimisation-coordinate
boxes. Every inverse search uses the frozen literal L-BFGS-B call and options.
A search succeeds only with normal optimizer success and a finite objective.
The audit is executable only when at least 12 of 16 searches succeed and at
least one returns `RMSE <= 5e-5` with scaled maximum natural-parameter distance
from the target below `0.01`.

A collision is any successful solution satisfying

```text
RMSE <= 5e-5
max_i(abs(theta_i - target_i) / support_width_i) >= 0.01.
```

A canonical audit passes only with no collision. These checks are supporting
local/noncollision evidence, explicitly not proof.

The residual/distance rule is fixed before simulation from a full dry-run
frontier. All nine canonical audits were executed over the grid
`{5e-5, 1e-4, 2e-4} x {0.0025, 0.005, 0.01}`. The unique passing candidate was
residual `5e-5` with scaled distance `0.01`. Target-recovery counts, ordered
`A/B/C`, were:

```text
dense      16 / 15 / 2
structured 16 / 14 / 3
sparse     15 / 16 / 16
```

All nine audits had no collision. A scaled distance of `0.01` defines
numerical equivalence within 1% of natural support width. This remains
supporting local/noncollision evidence only, not an identifiability proof.
Before any estimation, tests must reproduce all nine dry audits, these exact
recovery counts, and the no-collision result under the frozen objective,
starts, optimizer, rank, condition, and success rules.

Exact failure fixtures are:

1. `equal_emission_fixture`: dense schedule and real canonical design with
   `lambda_present = lambda_quasi = 1` in a control-specific unrestricted
   equal-rate evaluation. Process-parameter derivative columns must vanish and
   rank must be below `5`; no ordered transform or inverse search applies.
2. `deficient_design_fixture`: 32 synthetic cells, `Q = 0`, nonfinite `TP`,
   dense times `0, ..., 120`, and effort `1`; rank must be below `5`.
3. `absent_state_support_fixture`: 32 cells with `t_0` opportunities only and
   effort `1`; rank must be below `5`.

Controls pass as controls only by failing rank `5`; they cannot satisfy the
canonical audit. Any canonical dense, structured, or sparse audit failure
stops Goal 023 and returns to Barry; no schedule or estimand repair is permitted
under this namespace.

Every design diagnostic carries one provenance label and a distinct role:

- `potential_design` is the analyst preflight gate for every fit. It uses the
  analyst-visible unweighted `[1,G,Q]` over all potential intervals.
- `process_oracle_truth_at_risk` is a required
  `ORACLE-BENCHMARK-ONLY` gate for
  `process_oracle_observed_transition`. It uses oracle-only true at-risk rows
  and may fail that oracle layer, but it is never a joint acceptance input.
- `joint_plugin_smoothed_at_risk` is the analyst joint practical gate. At the
  fitted MLE, normalize the 21 event/censor path log weights for each cell. For
  interval `j = 1, ..., 20`, define

```text
w_xj = P_hat(Z_x,j-1 = 0 | analyst history)
      = sum(normalized path weights for event paths k >= j and censoring).
```

Use every cell/interval row `X = [1,G_endpoint,Q]` and compute rank/condition on
`float64 sqrt(W)X`. A failed or nonfinite joint fit makes the plug-in gate fail.
The plug-in gate is practical evidence, not structural evidence.

For each potential, oracle, or plug-in design diagnostic, `n_columns = 3` and
the generalized SVD convention above is applied to its `float64` unweighted or
weighted design matrix. Rank is an exact integer in
`0..min(n_rows,n_columns)`. Pass additionally requires
`n_rows >= n_columns`, rank `3`, and condition number below `1e8`.
Consequently `1x3/rank3` and `2x3/rank3` are impossible while `3x3/rank3` may
pass for potential, plug-in, or oracle provenance. Truth-at-risk rows never
enter joint starts, bounds, objective, profiles, diagnostics, or acceptance.

## Analyst/Truth Firewall

The deployable joint fitting interface may contain only:

- `cell_id`, `time`, `count`, and `effort`;
- standardised habitat quality `Q_x`; and
- fixed arrival time `TP(x)`.

Split, replicate, seed, and truth metadata remain in the benchmark controller
and evaluator; they are never passed to an estimator. The sole scenario-level
exception is an opaque module-issued `AnalystFitFrame` accepted by the joint
fitter. It is derived from the exact canonical fit-cell IDs, exposes only its
registered scenario, `analyst_fit` role, sorted IDs, count, and SHA-256, and is
validated before potential design construction or objective evaluation. The
objective still receives only the truth-free analyst batch. Separate
non-deployable oracle APIs may consume true transitions only for
`process_oracle_observed_transition` or
`observation_oracle_fixed_transition`. Tests must prove oracle truth cannot
enter joint fitting.

True states, true transition times, generating parameters, Goal 018 prey
abundance/extirpation, and reconstruction fields must live in a separate
evaluator object. Tests must prove that forbidden truth fields cannot influence
schedules, optimisation starts, bounds, seed assignment, fitting, or holdout
decisions.

## Pre-Simulation Amendment Governance

Task 2 remains stopped until all of the following hold simultaneously:

- replacement Goal, authoritative spec, Plan, and Runbook hashes are recorded
  and sealed;
- the source digest receipt remains unchanged at
  `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`;
- absence checks again prove no Task 2 files, simulation, seed namespace,
  calibration, Goal 023 artifacts, preholdout receipt, or holdout exposure;
- Task 1 terminology and API are polished by a fresh red-green cycle so
  numerical-domain failures are distinct from scientific likelihood outcomes,
  and frozen efforts/rates are proven comfortably inside the computational
  domain;
- Task 1 retains independent `ACCEPT` only for unchanged hashes
  `842908091c6a19f306db91cfef9f9c3d2f07eeb6062003c713fc0e4d5fc17309`
  (`tests/test_observe.py`) and
  `cfefe7ee14f0d9221fa73d96691c7b1657adbefa2f87f756c82c7019be73b74f`
  (`src/spatext/observe.py`); and
- fresh independent scientific-identifiability, executor-readiness, and
  provenance/freeze reviews all return `ACCEPT` with no Critical or Important
  findings.

Every scientific or provenance `ACCEPT` attached to an earlier document hash
is preserved as hash-specific and non-transferable. After this final contract
fix, scientific-identifiability, executor-readiness, and provenance/freeze
reviews are all `PENDING` for the new hashes.

Until those gates pass, this amendment changes documents only. No calibration
or holdout work is permitted.

## Scenario Contract

### Nested exact-model gates

1. `process_oracle_observed_transition`: true transition/censoring outcomes are
   supplied; fit only `alpha`, `beta_driver`, and `beta_quality`.
2. `observation_oracle_fixed_transition`: true transitions are fixed; fit only
   `lambda_present` and `lambda_quasi` under structured effort.
3. `dense_count_exact_model`: jointly fit all five parameters from counts at
   every passable cell and every six time units with effort `1`.
4. `structured_imperfect_effort`: jointly fit all five parameters at times
   `0, 12, ..., 120`; all passable cells remain opportunities and known effort
   is `0.7 + 0.6 * min(max((Q_x + 2) / 4, 0), 1)`.

### Expected failure and controls

5. `sparse_expected_failure`: a stable truth-independent 25% passable-cell
   frame, times `0, 24, ..., 120`, effort `0.6`.
6. `zero_driver_effect_negative_control`: exact model with generating
   `beta_driver = 0` and the normal `TP(x)` analyst covariate.
7. `permuted_arrival_alignment_stress`: positive-effect data generated with
   true `TP(x)`, then fitted with a deterministic cyclic permutation of `TP(x)`
   within row-band by habitat-quality-quintile blocks. Within each block, sort
   cells by integer `cell_id` and rotate the complete arrival-value vector,
   including nonfinite values, by `max(1, floor(block_size / 2))`. The
   permutation preserves block marginals while breaking cell-level alignment.
   Record Pearson correlation over pairs with finite true and permuted arrival;
   absolute correlation above `0.25` invalidates the stress contract.
8. `no_emission_contrast_negative_control`: generate
   `lambda_present = lambda_quasi = 1`; compare the ordered-emission fit to a
   separately defined equal-rate submodel with one `lambda_equal` parameter.
   Across the complete 24-replicate holdout scenario, fit one shared parameter
   vector by summing replicate log likelihoods. Use
   `D = 2 * (logLik_ordered - logLik_equal)` and a 199-bundle parametric
   bootstrap, each bundle containing 24 newly simulated replicates under the
   fitted equal-rate submodel. With
   `p = (1 + count(D_bootstrap >= D_observed)) / 200`, the control passes only
   when `p >= 0.05` and all 199 ordered bootstrap-bundle refits succeed. No
   profiles are computed. Structural status is determined by model degeneracy,
   never by bootstrap p: `lambda_present` has
   `structural_status = identified` because known-present `t_0` emissions
   identify its baseline level, and `practical_status = not_applicable` because
   this control computes no profile. `lambda_equal` in the equal submodel has
   both statuses `identified`, subject to a finite interior MLE. `alpha`,
   `beta_driver`, `beta_quality`, and `lambda_quasi` have both statuses
   `unidentified` for this scenario. The ordered
   `lambda_present/lambda_quasi` contrast is unidentifiable; the
   `lambda_present` baseline level itself is not. If `p < 0.05` or any ordered
   bundle refit fails, the control gate fails with `model_contract_failed`, but
   bootstrap outcome cannot change these structural labels.
9. `informative_dropout_misspecification_stress`: start from structured effort;
   remove opportunities with probability `0.10` while present and `0.45` after
   transition, then fit the ignorable-schedule model and classify resulting
   bias explicitly.
10. `goal018_continuous_abundance_stress`: use the structured schedule and
    Goal 018 continuous abundance interpolation. Generate
    `Y_xt ~ Poisson(E_xt * q * N_xt)` with
    `q = 4 / mean(N_xt over finite positive structured opportunities)`, then
    fit the binary model. No parameter-recovery claim is made; a predictive
    lack-of-fit warning is required.
11. `spatial_frailty_stress`: start from the exact structured model, generate
    an iid standard-normal `72 x 84` field, smooth it with
    `scipy.ndimage.gaussian_filter(sigma=6, mode="reflect")`, standardise over
    passable cells, and multiply observation intensity only by
    `exp(0.5 * U_x - 0.125)`. Fit the independent-cell model.

Failures must be attributed to process, observation, joint recovery,
information limitation, or misspecification rather than collapsed into one
score.

## Integrated Pre-Task-3 Contract Amendment

This integrated pre-Task-3 amendment changes no Goal 023 biological or
statistical model equation, estimand, natural support, generating value,
transition or emission timing convention, optimizer/profile rule, scenario ID,
schedule, effort rule, replicate count, predictive-reference count, bootstrap
count, seed payload or substream mapping, existing numerical recovery/coverage/
predictive threshold, transportability statement, or publication authority.
It adds descriptive latent diagnostics, total decision handling, typed evidence
identity, nonrecursive artifact hashes, fixture-only Task 3 dispatch, and
fail-closed provenance execution mechanics only.

### Scenario Evidence Registry And Fit Identity

The following 11-row registry is literal and ordered. It is the only authority
for truth access, fit scope, primary fit variant, comparator fit variant, and
latent-time applicability. Comparator fits remain visible in
`fit_execution_evidence.csv` but never silently enter primary recovery,
coverage, profile, latent-time, or predictive rows.

| # | Scenario | Truth access | Fit scope | Primary variant | Comparator | Parameter evidence | Latent-time evidence |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `process_oracle_observed_transition` | `oracle_only` | `replicate` | `canonical` | none | gated, 3 process parameters | diagnostic, all 5,225 passable cells |
| 2 | `observation_oracle_fixed_transition` | `oracle_only` | `replicate` | `canonical` | none | gated, 2 rates | not applicable |
| 3 | `dense_count_exact_model` | `analyst_firewalled` | `replicate` | `canonical` | none | gated, 5 parameters | diagnostic, all 5,225 passable cells |
| 4 | `structured_imperfect_effort` | `analyst_firewalled` | `replicate` | `canonical` | none | gated, 5 parameters | diagnostic, all 5,225 passable cells |
| 5 | `sparse_expected_failure` | `analyst_firewalled` | `replicate` | `canonical` | none | dedicated `beta_driver` gate; other rows descriptive | diagnostic, fixed 1,306-cell sparse frame |
| 6 | `zero_driver_effect_negative_control` | `analyst_firewalled` | `replicate` | `canonical` | none | control plus descriptive recovery | diagnostic, all 5,225 passable cells |
| 7 | `permuted_arrival_alignment_stress` | `stress_evaluator_only` | `replicate` | `permuted_alignment` | `correct_alignment` | primary variant descriptive; comparator score only | diagnostic, fixed 1,045 score cells |
| 8 | `no_emission_contrast_negative_control` | `analyst_firewalled` | `scenario_shared` | `equal_rate` | `ordered_emission` | shared fits and six fixed status rows; no recovery/profile rows | not applicable |
| 9 | `informative_dropout_misspecification_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | descriptive, 5 known parameters | diagnostic, all 5,225 passable cells |
| 10 | `goal018_continuous_abundance_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | estimates/interval widths only; no recovery truth | not applicable |
| 11 | `spatial_frailty_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | descriptive, 5 known parameters | diagnostic, all 5,225 passable cells |

Truth-access meanings are literal:

- `oracle_only`: true transition/state fields may enter only the physically
  separate named oracle likelihood. They never enter joint fitting.
- `analyst_firewalled`: generation truth remains in the controller/evaluator;
  the fitted interface receives only analyst-visible fields. Evaluation may
  compare a completed fit with generating truth.
- `stress_evaluator_only`: stress construction, hidden state, original
  alignment, dropout, frailty, continuous abundance, and correct/permuted
  comparison state remain in a physically separate evaluator and are consulted
  only after the required fit has completed.

For the arrival stress, the permitted permuted `TP(x)` is the primary analyst
covariate and true `TP(x)` is permitted only in the separate correct-alignment
comparator. Original alignment, permutation audit, paired-score evaluation, and
truth-based descriptive rows remain evaluator-only. For zero-driver and
equal-emission controls, the fitter is never told the generating zero/equal
label through starts, bounds, objectives, profiles, or tie-breaking.

Truth may generate data, compute a preregistered post-fit truth diagnostic, and
assign a frozen gate. It must never alter analyst schedules, starts, bounds,
objectives, profile starts, plug-in weights, predictive references, sorting, or
fit classification.

### Latent-Transition Diagnostics

Latent-time metrics are proper or interpretable censor-aware diagnostics, not
Goal 023 acceptance gates. They add no quantitative threshold, do not alter any
nested or scenario gate, and are excluded from recommendation inputs. An
available applicable row and an unavailable applicable row both use
`gate_result=diagnostic`; availability is carried separately. An inapplicable
row uses `gate_result=not_applicable`.

Index the 21 transition paths by `r=1,...,21` and define ordered evaluation
values `v_r=6*r`. Values `v_1,...,v_20` are event endpoints `6,...,120`.
`v_21=126` is an ordered label for `T>120`, not a biological claim that a
censored event occurred at 126.

For cell `x`, evaluator truth is

```text
R_x = transition_time / 6  for transition_time in {6,...,120}
R_x = 21                   for right censoring after 120
U_x = v_(R_x).
```

Let `p_xr` be the normalized analyst-side probability of path `r` at the
plug-in fit. These are conditional latent-path weights, not parameter-posterior
samples and not an MCMC/full-Bayesian posterior.

For process oracle, construct `p_xr` from fitted process path masses using only
analyst-visible `Q_x` and `TP(x)`. Complete that matrix before supplying true
event/censor outcomes to the evaluator. Never replace it with a one-hot oracle
truth vector. For ordinary joint fits, use normalized batched analyst path
weights at the fitted MLE. Evaluator truth enters only the pure scoring kernel.

Require exact sorted integer cell IDs on analyst and evaluator sides, exact
one-to-one ID equality, a `float64` matrix of shape `(N,21)`, finite nonnegative
entries, and every row sum within `1e-12` of one. Divide a within-tolerance row
by its finite positive sum once; do not clip or discard censor mass. Require
finite event truth on `6,12,...,120` or the accepted censor sentinel. A
missing/extra/duplicate cell, invalid probability, invalid truth, or nonfinite
score makes all three replicate diagnostics unavailable; no cell is dropped.

For endpoint `j=1,...,20`, define

```text
F_xj = sum(p_xr for r <= j)
I_xj = 1 if R_x <= j else 0.
```

The cumulative-incidence Brier diagnostic is

```text
transition_brier.observed_value =
  sum_x sum_j (F_xj - I_xj)^2 / (20*N)

transition_brier.expected_value =
  sum_x sum_j F_xj*(1-F_xj) / (20*N)

transition_brier.error = observed_value - expected_value.
```

It lies in `[0,1]` and is strictly proper for the complete ordered 21-category
distribution because the 20 cumulative probabilities identify all path masses.

Fix `alpha_interval=0.10`. Define the deterministic lower discrete quantile

```text
Q_x(q) = min(v_r such that sum(p_xs for s <= r) >= q).
```

Set `L_x=Q_x(0.05)` and `H_x=Q_x(0.95)`. Define the positively scaled central
interval score

```text
S_x(u) = 0.05*(H_x-L_x)
         + (L_x-u)*1(u<L_x)
         + (u-H_x)*1(u>H_x)

transition_interval_score.observed_value = sum_x S_x(U_x)/N
transition_interval_score.expected_value =
  sum_x sum_r p_xr*S_x(v_r)/N
transition_interval_score.error = observed_value - expected_value.
```

It lies in `[0,120]` time units and is proper for the 5th and 95th quantiles.
The positive `0.05` scale is part of the formula.

Set `M_x=Q_x(0.50)` and `A_x=abs(U_x-M_x)`. Then

```text
transition_median_absolute_error.observed_value = ordinary_median(A_1,...,A_N)
B_x = sum_r p_xr*abs(v_r-M_x)
transition_median_absolute_error.expected_value = ordinary_median(B_1,...,B_N)
transition_median_absolute_error.error = observed_value - expected_value.
```

For even `N`, the ordinary median is the arithmetic mean of the two central
sorted values. The median absolute error is an interpretable resolution
diagnostic, not a strictly proper full-distribution score, and its error is a
resolution contrast rather than a calibration residual with a claimed null
distribution.

Applicability and cell denominators are literal:

| Scenario | Status | `sample_size` | Frame/variant |
| --- | --- | ---: | --- |
| `process_oracle_observed_transition` | applicable | `5225` | all passable cells, canonical process fit |
| `observation_oracle_fixed_transition` | not applicable | `0` | none |
| `dense_count_exact_model` | applicable | `5225` | all passable cells, canonical fit |
| `structured_imperfect_effort` | applicable | `5225` | all passable cells, canonical fit |
| `sparse_expected_failure` | applicable | `1306` | frozen sparse frame, canonical fit |
| `zero_driver_effect_negative_control` | applicable | `5225` | all passable cells, canonical fit |
| `permuted_arrival_alignment_stress` | applicable | `1045` | score frame, primary permuted fit only |
| `no_emission_contrast_negative_control` | not applicable | `0` | none |
| `informative_dropout_misspecification_stress` | applicable | `5225` | all passable cells, canonical fit |
| `goal018_continuous_abundance_stress` | not applicable | `0` | no Goal 023 binary transition truth |
| `spatial_frailty_stress` | applicable | `5225` | all passable cells, canonical fit |

For every scientifically scheduled scenario/split/replicate, emit exactly
three rows in metric order `transition_brier`,
`transition_interval_score`, `transition_median_absolute_error`. Do not create
rows for a split the scenario does not instantiate. Inapplicable rows have
`sample_size=0`, `fit_succeeded=null`, `diagnostic_available=false`, null
numeric fields, and `gate_result=not_applicable`.

Applicable rows always retain the frozen cell denominator. All censored cells
remain in `N`. Missing count opportunities remove emissions only, never cells,
transition intervals, censor mass, or evaluator truth. Informative-dropout
cells with no retained counts receive an empty analyst history and fitted
process path probabilities.

A successful finite applicable fit with valid posterior/truth input has
`fit_succeeded=true`, `diagnostic_available=true`, finite values, and
`gate_result=diagnostic`. A failed/nonfinite required fit has
`fit_succeeded=false`, `diagnostic_available=false`, null numeric fields, the
fixed `sample_size`, and `gate_result=diagnostic`. A successful fit with an
invalid probability matrix, truth mismatch, or failed prerequisite design has
its literal fit status, `diagnostic_available=false`, null numeric fields, the
fixed `sample_size`, and `gate_result=diagnostic`. No complete-case fallback is
allowed.

A missing profile alone does not prevent plug-in path scoring when the MLE is
finite; the separate profile/recovery gate retains its own failure. A latent
row may not enter starts, fitting, profiles, plug-in design, predictive
references, scenario reducers, recommendation precedence, or result selection.
Missing, duplicate, malformed, or orphan latent rows are an artifact/schema
contract failure; their scientific values and availability are not.

### Total Recommendation Contract

#### Common Evidence States

Insert these definitions before the scenario decision table:

```text
available       required evidence is converged, finite, schema-valid, and applicable
nonconverged    attempt exists but fails the frozen fit-success contract
nonfinite       a required value is nonfinite and serialized null with a typed flag
open_profile    valid profile reaches support without a closing crossing
missing_result  required row/variant/profile/diagnostic was not emitted
not_applicable  authority explicitly excludes the output
```

A missing/duplicate attempted row is `missing_result`, never an open profile.
Predictive completeness requires a successful finite required fit and all 27
valid diagnostic cells for every attempted replicate. A scientific warning
exists only when predictive evidence is complete and a finite preregistered
warning rule fires. Forced warning due to unavailability cannot satisfy a
stress warning requirement.

#### Frozen Denominators And Missingness

The following rules are patch text and do not alter existing numeric gates:

```markdown
For nested scenarios 1-4, use all 48 attempted holdout replicates for every
applicable parameter. Convergence denominators remain 48. Coverage is a
48-element Boolean vector; a nonconverged/nonfinite fit or open/missing interval
is uncovered. Missing estimates and interval widths receive the existing full-
support imputations `8`, `6`, `4`, `0.99`, or `9.75`. Median and maximum
absolute error and width use all 48 imputed values; the even median averages
positions 24 and 25. Signed-error medians use finite converged estimates only
and are null when none exist. Coverage remains inclusive `36..48`; convergence
minima remain `46/48`, `46/48`, `46/48`, and `44/48` in scenario order. A
missing or duplicate row is an artifact/schema failure and is never imputed.

Sparse honesty uses all 24 attempted `beta_driver` rows:

```text
sparse_coverage_pass = 18 <= coverage_count <= 24
sparse_width_pass = sparse_imputed_median_width >= structured_imputed_median_width
sparse_honesty_pass =
    sparse_predictive_pass and sparse_coverage_pass and sparse_width_pass.
```

Nonconverged/nonfinite/open/missing intervals are uncovered and contribute
width `6`; average sorted one-based positions 12 and 13. A failed required fit
also fails predictive completeness and cannot be rescued by imputation. Width
equal to structured passes; any smaller value is
`sparse_unexpectedly_narrow`. Other sparse recovery summaries are descriptive.

Zero-driver availability and false signal are separate:

```text
interval_decidable =
    fit is successful and finite
    and both interval endpoints are finite and closed
excludes_zero = interval_lower > 0 or interval_upper < 0
zero_driver_availability_pass = decidable_interval_count == 24
zero_driver_false_signal_pass =
    zero_driver_availability_pass and 0 <= exclusion_count <= 6.
```

A touching interval contains zero. An undecidable attempt has
`excludes_zero=null`, remains in the denominator, and prevents the binomial
decision.

Arrival uses 24 paired attempts. A pair requires successful finite correct and
permuted fits plus finite fixed-frame heldout scores. A failed pair is no win
and fails availability. Correlation must be finite and absolute value at most
`0.25`. With complete availability, `22..24` strict correct-score wins pass and
`0..21` fail discrimination. The primary permuted fit supplies profiles and
predictive references; the correct fit is comparator evidence only. At least
one available scientific warning is mandatory.

Equal emission uses one shared equal and one shared ordered fit over all 24
replicates and exactly 199 complete 24-replicate bootstrap bundles. The add-one
denominator remains 200. Any failed/nonfinite shared fit, statistic, equal fit,
or ordered refit fails availability. With complete availability, `p>=0.05`
passes and `p<0.05` fails. No profile rows exist. The six fixed status rows are
independent of p and exempt from generic accepted-estimand confounding because
unidentifiability is the expected control result.

Every predictive-applicable attempted replicate emits exactly 27 stable rows.
A failed fit emits 27 unavailable rows, no reference ensemble, remains in the
full denominator, increments `failed_fit_count`, and fails predictive
completeness. Nonfinite diagnostics serialize null plus the existing flag.

For informative dropout and spatial frailty, retain all 24 descriptive rows per
known parameter. Coverage uses 24 attempts; failed/nonfinite/open/missing
intervals are uncovered; descriptive error/width uses existing full-support
imputation; signed error remains finite-only. `narrow_wrong` is true only for a
finite closed two-sided interval excluding truth with width no larger than the
existing parameter maximum. Open and broad wrong intervals are not
`narrow_wrong`. No new stress recovery threshold is added.

Continuous abundance has no parameter-recovery truth. Its fit/profile rows are
descriptive with null truth, coverage, error, and `narrow_wrong`; its decisive
scientific requirement is complete predictive evidence with at least one
warning.
```

#### Total Scenario Decision Table

Evaluate global contract gates first, then scenarios in canonical order. Within
one scenario, the first matching row has local precedence. Compute all local
reasons for reporting, then reduce by global rank.

| # | Scenario | First matching condition | Local impact and canonical reason |
| ---: | --- | --- | --- |
| 1 | process oracle | Any potential/oracle design, convergence, coverage, existing error/width, fit-domain, or required artifact gate fails | `contract_failure:process_oracle_failed` |
| 1 | process oracle | All applicable gates pass | `pass` |
| 2 | observation oracle | Any potential design, convergence, coverage, existing error/width, fit-domain, or required artifact gate fails | `contract_failure:observation_oracle_failed` |
| 2 | observation oracle | All gates pass; conditional prediction may warn diagnostically | `pass` |
| 3 | dense exact | Missing/duplicate/malformed evidence, numerical-domain failure, or predictive evidence unavailable for a reason other than a retained typed nonconvergence | `contract_failure:dense_evidence_invalid` |
| 3 | dense exact | With complete schema-valid finite evidence after both oracles pass, any dense convergence, coverage, existing accuracy/precision, finite plug-in design, accepted-estimand identification, or exact predictive scientific gate fails; typed nonconvergence-driven incompleteness is included | `confounding:dense_joint_failed` |
| 3 | dense exact | All dense gates pass | `pass` |
| 4 | structured exact | Missing/malformed evidence; required-fit unavailability; convergence failure; coverage outside `36..48`; predictive incompleteness/rejection; or plug-in design unavailable, rank below `3`, nonfinite, or condition `>=1e8` | `contract_failure:structured_not_calibrated` |
| 4 | structured exact | Complete valid evidence declares an accepted estimand structurally or practically unidentified, excluding expected equal-emission labels | `confounding:structured_estimand_unidentified` |
| 4 | structured exact | Coverage, fit availability, plug-in design, accepted-estimand identification, and prediction pass, but an existing median error or median width limit fails | `structured_limitation:structured_precision_recovery_failed` |
| 4 | structured exact | Every structured gate passes | `pass` |
| 5 | sparse | Missing/malformed rows, required-fit/predictive failure, coverage outside `18..24`, or median width below structured | `contract_failure:sparse_honesty_failed` |
| 5 | sparse | Coverage, width, and predictive completeness pass | `pass` |
| 6 | zero driver | Any interval undecidable, required fit/plug-in/predictive evidence fails, or rows are missing/malformed | `contract_failure:zero_driver_unavailable` |
| 6 | zero driver | All 24 intervals decidable and exclusions are `7..24` | `confounding:zero_driver_false_signal` |
| 6 | zero driver | All intervals decidable, exclusions `0..6`, and standard prediction passes | `pass` |
| 7 | arrival alignment | Invalid/nonfinite correlation; missing pair; required fit/plug-in/score/predictive unavailability; or malformed evidence | `contract_failure:alignment_contract_or_availability_failed` |
| 7 | arrival alignment | Complete valid evidence but no available scientific warning | `contract_failure:alignment_silent_misspecification` |
| 7 | arrival alignment | Complete evidence and warning, but correct alignment wins `0..21` | `confounding:arrival_alignment_not_discriminated` |
| 7 | arrival alignment | Correlation valid, all 24 pairs available, wins `22..24`, and warning present | `pass` |
| 8 | equal emission | Shared fit/statistic invalid; any of 199 ordered refits fails; p nonfinite or `<0.05`; fixed status differs; or evidence malformed | `contract_failure:equal_emission_control_failed` |
| 8 | equal emission | All refits succeed, p `>=0.05`, and fixed statuses are exact | `pass` |
| 9 | informative dropout | Required fit/plug-in/predictive evidence unavailable or malformed | `contract_failure:informative_dropout_unavailable` |
| 9 | informative dropout | `any_narrow_wrong=true` and no available scientific warning | `contract_failure:informative_dropout_silent_misspecification` |
| 9 | informative dropout | Prediction complete and either no narrow-wrong result exists or a warning detects it | `pass` |
| 10 | continuous abundance | Required fit/plug-in/predictive evidence unavailable or malformed | `contract_failure:continuous_abundance_unavailable` |
| 10 | continuous abundance | Complete evidence but no available scientific warning | `contract_failure:continuous_abundance_silent_misspecification` |
| 10 | continuous abundance | Complete evidence and at least one warning | `pass` |
| 11 | spatial frailty | Required fit/plug-in/predictive evidence unavailable or malformed | `contract_failure:spatial_frailty_unavailable` |
| 11 | spatial frailty | `any_narrow_wrong=true` and no available scientific warning | `contract_failure:spatial_frailty_silent_misspecification` |
| 11 | spatial frailty | Prediction complete and either no narrow-wrong result exists or a warning detects it | `pass` |

Latent diagnostic values, expected values, residuals, and availability never
appear in this table. A missing/duplicate/malformed latent artifact row may fail
the global artifact/schema contract, but a large, small, or unavailable
scientific latent diagnostic cannot change a local impact.

## Replication And Holdout Lock

- Master seed: `20260711`.
- Every stochastic component uses its own canonical payload and independent
  substream. The payload is compact sorted-key ASCII JSON with exactly the keys
  `goal`, `master_seed`, `scenario_id`, `split`, `replicate_index`,
  `component`, and `draw_index`. `goal` is the string `"023"`; `draw_index` is
  JSON `null` when absent. Missing, unknown, or extra keys fail validation.
- Allowed component labels are exactly `schedule`, `process`, `observation`,
  `dropout`, `frailty`, `predictive_reference`, `bootstrap`, and
  `pit_randomization`. Base `process`, `observation`, `dropout`, `frailty`,
  `schedule`, and `pit_randomization` payloads require `draw_index = null`;
  `predictive_reference` and `bootstrap` require an integer draw index in
  `0, ..., 198`. Unknown component/index combinations fail validation.
- All indices are zero-based and literal. The four nested scenarios use
  development `replicate_index = 0, ..., 11`, calibration
  `replicate_index = 0, ..., 23`, and holdout
  `replicate_index = 0, ..., 47`. `sparse_expected_failure`, controls, and
  stresses use development `replicate_index = 0, ..., 11` and holdout
  `replicate_index = 0, ..., 23`, with no calibration rows. Predictive
  references use `draw_index = 0, ..., 198`. The scientific equal-emission
  bootstrap uses bundle `draw_index = 0, ..., 198` and pseudo-replicate
  `replicate_index = 0, ..., 23`. Apart from the explicitly frozen timing-only
  equal-emission development exception below, unknown
  scenario/split/component combinations and every out-of-range index fail
  before RNG construction. Artifact `replicate_id` values equal these payload
  `replicate_index` values exactly.
- SHA-256 is computed over the canonical JSON's UTF-8 bytes. Interpret the
  digest as eight consecutive big-endian `uint32` entropy words, pass those
  words to `numpy.random.SeedSequence`, and construct
  `Generator(PCG64DXSM(seed_sequence))`.

Frozen non-holdout test vectors use `bit_generator.random_raw(3)` for the first
three `uint64` draws:

```text
payload={"component":"process","draw_index":null,"goal":"023","master_seed":20260711,"replicate_index":0,"scenario_id":"dense_count_exact_model","split":"development"}
sha256=e7928c352cbc24709b93269d85cfc8f01747268704eac132e91ce65be474a87d
entropy_words=[3885141045,750527600,2610112157,2244987120,390538887,82493746,3910985307,3832850557]
first_uint64=[10510340404464842761,2174300553185413078,258851366587855250]

payload={"component":"predictive_reference","draw_index":0,"goal":"023","master_seed":20260711,"replicate_index":7,"scenario_id":"structured_imperfect_effort","split":"calibration"}
sha256=2acf57050eb0d734bd138eb6780be7998f2c55abc568fc769125f6e0616fabce
entropy_words=[718231301,246470452,3172175542,2014046105,2402047403,3311991926,2435184352,1634708430]
first_uint64=[11123817839291538733,6431681636083337449,10453666639700693841]
```

No holdout payload may be instantiated during this amendment or its document
checks. Only development and calibration vectors are permitted before the
replacement contract is independently sealed.

### Canonical stochastic realisation and schedules

Canonical passable cells are sorted by integer `cell_id`, model times are
ascending, and opportunities are sorted by integer `cell_id` then time.
Stochastic consumption is fixed:

- the base process generator makes one `float64` uniform array with shape
  `(n_passable, 20)` in C order and consumes every entry even after absorption;
- the base observation generator makes one `numpy.Generator.poisson` call over
  the complete canonical mean vector with shape `(n_opportunities,)`, with no
  state-dependent skipping;
- the dropout generator makes one complete canonical uniform vector for every
  structured opportunity before filtering;
- the frailty generator makes one `standard_normal` array with shape `(72,84)`
  in C order, smooths it, then standardises over passable cells with `ddof=0`;
- each predictive-reference draw consumes its complete process uniform array
  first, then its complete canonical Poisson vector; and
- scientific bootstrap bundle `b = 0, ..., 198` and pseudo-replicate
  `r = 0, ..., 23` use `component="bootstrap"`, `split="holdout"`,
  `replicate_index=r`, and `draw_index=b`; each generator consumes the process
  array then observation vector.

The last bullet freezes future holdout mapping only. No holdout payload or
vector may be instantiated during amendment, implementation tests,
development, or calibration.

The sparse frame is fixed across every split and replicate. For each passable
cell, hash ASCII
`"023|sparse_expected_failure|cell_id=<integer>"` with SHA-256; sort by digest
then integer `cell_id`; retain the first
`floor(0.25 * 5225) = 1306` cells. No RNG or truth enters frame selection.

Scenario schedules are literal:

| Scenario | Schedule | Effort |
| --- | --- | --- |
| `process_oracle_observed_transition` | `process_truth`, no counts | not applicable |
| `observation_oracle_fixed_transition` | `structured_12` | structured formula |
| `dense_count_exact_model` | `dense_6` | `1` |
| `structured_imperfect_effort` | `structured_12` | structured formula |
| `sparse_expected_failure` | `sparse_24` | `0.6` |
| `zero_driver_effect_negative_control` | `dense_6` | `1` |
| `permuted_arrival_alignment_stress` | `structured_12` | structured formula |
| `no_emission_contrast_negative_control` | `dense_6` | `1` |
| `informative_dropout_misspecification_stress` | `structured_12` | structured formula before dropout |
| `goal018_continuous_abundance_stress` | `structured_12` | structured formula before stress generation |
| `spatial_frailty_stress` | `structured_12` | structured formula before frailty |

The structured formula remains
`0.7 + 0.6 * min(max((Q_x + 2) / 4, 0), 1)`.

Assign quality quintiles by ranking every passable cell on `(Q_x, cell_id)`.
For zero-based rank `r` among `n = 5225`, set
`quintile = min(5, 1 + floor(5 * r / n))`, labelled `q1, ..., q5`.

Arrival-permutation blocks are published Goal 017 `row_band` crossed with this
quality quintile. Within a block, sort integer `cell_id`, set
`shift = max(1, floor(block_n / 2))`, and assign
`permuted[i] = original[(i + shift) % block_n]`, including nonfinite arrivals.

The alignment score frame is fixed analogously: hash ASCII
`"023|alignment_score|cell_id=<integer>"`, sort by digest then integer
`cell_id`, and use the first `floor(0.20 * 5225) = 1045` cells for scoring and
the rest for fitting. Fit correct and permuted models only on fit cells; score
marginal joint log likelihood only on score cells. Correct alignment must win
at least `ceil(0.90 * 24) = 22` holdout replicates.

For randomized PIT, create one `pit_randomization` generator per
scenario/split/replicate with `draw_index = null` and consume uniforms in the
frozen stratum then metric order defined in the predictive-gate section.
- Nested exact-model scenarios use `12` development, `24` calibration, and
  `48` untouched holdout replicates each.
- `sparse_expected_failure` uses all `24` untouched holdout replicates for its
  dedicated `beta_driver` honest-coverage gate.
- Controls and stresses use `12` development and `24` untouched holdout
  replicates each, with no calibration rows.
- Predictive references use one `199`-dataset ensemble per fitted replicate,
  reused across every stratum and metric. The equal-emission scenario-level
  bootstrap uses `199` 24-replicate bundles.
- Holdout rows cannot be generated or read before the authoritative spec and
  calibration config hashes are reviewed and frozen.
- Immediately before holdout, canonically hash every analytical tracked file;
  exclude only append-only `Log.md` and the self-referential receipt files
  `preholdout_state_receipt.json` and `holdout_receipt.json`. Store the file manifest
  and aggregate `tracked_state_sha256` in the frozen config and tracked
  `preholdout_state_receipt.json`. The holdout command and every later gate
  must reproduce this hash.
- Any equation, parameter, bound, scenario, seed, replicate, interval, or gate
  change after holdout exposure invalidates the holdout. Continuing then needs
  a fresh untouched seed namespace and Barry's approval.
- The holdout command must create the tracked immutable receipt
  `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json`
  atomically before emitting holdout results. A pre-existing receipt makes a
  second holdout execution fail.
### Provenance Amendment Contract

This provenance amendment changes no scientific contract or result. The pinned
repository identity is branch
`codex/spatext-goal023-latent-response-observation-gate`, HEAD
`53462d0365babf2c8070714a930f69b4071af276`, and base ref `origin/main`
resolving to the same commit.

The external authority tuple is independently reconstructed from live disk at
every guarded boundary. Hash the exact regular authoritative spec file
`spec/synth_medium_latent_response_observation_recovery_gate.md` for
`spec_sha256`. Read the exact regular accepted
`source_digest_receipt.json`; its complete file SHA-256 must equal
`5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`,
its declared and independent landscape hashes must match, its declared and
independent arrival hashes must match, `passed` must be true, and its source
commit and parameter-set identity must remain the accepted literals. Derive
`source_sha256` from those parsed landscape/arrival values with the formula
below. A caller-supplied or merely cross-consistent authority tuple is never a
substitute for this reconstruction.

At config emission, freeze, holdout pre-create, holdout post-create, and the
immediate-pre-RNG guard, the config, preholdout receipt when present, and
holdout receipt when present must each equal the freshly reconstructed live
`spec_sha256` and `source_sha256`, as well as the captured analytical digest
and literal tracked manifest. Validate the complete payload and every
cross-binding before opening an exclusive output file. Any pre-create failure
creates no file. A failure after exclusive creation never deletes, truncates,
replaces, or retries that file; it preserves the created bytes and returns the
explicit immutable stop disposition for config, preholdout receipt, or
post-exposure holdout receipt. Existing bytes are always preserved.

Config emission, `freeze-tracked-state`, and the holdout phase immediately
before exclusive receipt creation and again immediately before any RNG object
or payload construction must fail closed unless all of the following hold:

1. branch, HEAD, and base are exact;
2. the literal 16-file analytical manifest is complete and reproduces its
   digest;
3. every changed candidate path is inside the literal Runbook section 8
   19-path publication-path universe;
4. every path required in the current phase is present with its exact disk hash
   and every receipt required to be absent in that phase is absent;
5. no untracked non-ignored path exists outside that allowlist and no other
   out-of-footprint path exists; and
6. the phase-specific config and receipt conditions hold.

The phase-specific presence vector is literal:

```text
config emission and pre-freeze:
  present = 16 analytical files + Log.md
  absent  = preholdout_state_receipt.json + holdout_receipt.json

post-freeze and holdout pre-receipt:
  present = 16 analytical files + Log.md + preholdout_state_receipt.json
  absent  = holdout_receipt.json

holdout post-receipt and publication:
  present = all 19 publication paths
  absent  = none
```

The accepted candidate-footprint rule permits required new publication paths
to remain unstaged before the existing section 8 exact-staging step; it does not
permit an unknown path. The guard records each candidate path's exact status,
presence/absence, and disk hash so a new, removed, staged, unstaged, or
untracked state change cannot be hidden.

A config-emission failure writes no config. A freeze failure changes no config
byte and creates no preholdout receipt. A pre-receipt failure creates no
holdout receipt. A post-receipt/pre-RNG failure preserves the immutable
receipt, constructs no RNG object or payload, burns the namespace, and records
`STOP_INVALIDATED_POST_EXPOSURE`.

Before freeze, every potentially mutating validation command, including
`pre-commit run --all-files`, must be proven a working-tree and index no-op on
the exact candidate. Any pre-freeze mutation returns to RED-GREEN work, config
re-emission, hash resealing, and fresh review.

After exclusive atomic holdout-receipt creation, working-tree writes to tracked
publication paths are limited to that machine-created immutable receipt and
append-only provenance records at the end of Goal 023 `Log.md`. The Log
authorization is explicit and independent of the scientific-command output
restriction. One designated provenance writer may append only an independently
approved exact payload. No other tracked working-tree write is authorized.

A Log append must reproduce its parent line count, byte count, and SHA-256;
preserve every parent byte as an exact prefix; bind branch/HEAD/base, authority
tuple, embedded and file config hashes, analytical digest, both receipt file
hashes and embedded receipt self-hash, represented artifact-set hash, complete
artifact-set hash, and current candidate/index manifests; identify writer and
reviewer roles plus immutable disposition; and change no analytical contract or
artifact result.

Every command started after exposure, including inspection, hashing,
validation, review preparation, staging, provenance append, commit, merge,
fetch, push, and publication guards, runs inside its own fail-closed
before/after envelope. Immediately before each command capture:

- branch, HEAD, and base;
- complete tracked, staged, unstaged, and untracked non-ignored status;
- the cached path/blob manifest;
- the literal 16-file path/hash manifest and aggregate digest;
- current Log byte count, line count, SHA-256, and exact prefix bytes;
- existence and full-file SHA-256 of both receipts;
- embedded `receipt_sha256` for the holdout receipt;
- embedded `config_sha256` and complete `config_file_sha256`;
- the represented 21-file artifact manifest and
  `represented_artifact_set_sha256`; and
- the exact lexical 22-file path/hash snapshot, including
  `verification.json`, plus `artifact_set_sha256`.

Immediately after the command reproduce every immutable member. A missing,
added, replaced, reordered, zero-byte, nonregular, or changed artifact is a
mutation. Apply the envelope separately to each command, never once around a
batch.

For an authorized Log append, the old Log bytes must remain the exact prefix
and the suffix must equal the independently approved payload byte for byte.
Every other envelope member and every non-Log index blob remains unchanged.
For an authorized exact staging command, only the index may change, and only to
the predeclared allowlisted path/blob set; no working-tree byte may change. The
authorized commit may change only HEAD from the pinned parent to a commit whose
parent and complete tree equal the approved parent and cached candidate.
Subsequent fast-forward and push commands may make only the exact identity
transitions in Runbook section 9. All other commands leave Log, index,
identity, status, footprint, receipts, config, and artifacts unchanged.

An ordinary provenance Log suffix is canonical JSON whose complete envelope
bindings are parsed and recomputed by the validator. No caller boolean can
assert that an arbitrary suffix binds the envelope. Retry authorization must
freshly capture the current complete envelope, bind the exact failed command
and exit record, and consume the module-validated reviewed Log-only transition
from the failure envelope to that current envelope. Any other intervening
identity, byte, status, config, receipt, artifact, candidate, or index change
rejects retry.

The exact-staging validator captures the literal worktree blob map, the literal
index blob map, and the real `git write-tree` identity after all 19 paths are
staged. It returns a module-issued validated staging identity. Commit, merge,
and push transition validation takes that identity, not a caller-supplied tree,
and requires every captured commit tree to equal its `git write-tree` value.

Fixture artifact emission accepts only a module-issued temporary fixture root.
The issuer resolves both the requested path and the canonical production path
`artifacts/synth_medium_latent_response_observation_recovery`; it rejects that
path and every resolved alias before any directory or file write. A raw path,
non-temporary path, forged root token, moved alias, or canonical descendant is
invalid. Fixture dispatch remains unable to reach RNG, live calibration,
holdout payload, scientific rows, or canonical output services.

All ordinary post-holdout review records are appended and staged before final
review. The final reviewer inspects the exact cached candidate and an exact
proposed terminal-attestation payload containing its live Log parent. On
acceptance, that returned payload is the approved append. The provenance writer
appends it once, stages `Log.md`, proves exact prefix and suffix plus unchanged
non-Log blobs and envelope, and permits no further Log append before commit. No
second attestation about that append is permitted. Rejection appends no
acceptance record.

The holdout command internally repeats the complete frozen-state guard after
receipt creation and before RNG construction. After successful emission it
establishes the immutable 22-file artifact snapshot used by every later
envelope.

A zero exit with an unchanged envelope is
`CONTINUE_FROZEN_CANDIDATE`. Any byte, identity, status, or footprint mutation
is `STOP_INVALIDATED_POST_EXPOSURE`, whether the command exits zero or nonzero:
preserve state, receipts, config, and artifacts; append the stop disposition if
the Log prefix remains safely appendable; do not restore, repair, amend, or
retry under the namespace.

A nonzero exit with an otherwise unchanged envelope is
`STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION`. It does not
scientifically invalidate the frozen result, but validation is unsatisfied and
publication pauses. One retry is permitted only for the exact same
non-generative validation command after an independent executor-readiness
reviewer records that the first failure was transient, confirms the complete
envelope remained unchanged, and approves the exact retry command.

No edit, dependency change, environment mutation, cleanup, regeneration,
calibration, holdout execution, RNG command, or artifact-producing command may
occur between attempts. The sole permitted intervening command is one
authorized exact Log append recording the independent transient classification
and exact retry. That append advances only the guarded Log prefix. Holdout and
all scientific or artifact-generating commands are never retryable.

If the one retry exits zero with an unchanged envelope, record
`CONTINUE_FROZEN_CANDIDATE`. If it again exits nonzero without mutation,
record `STOP_NONMUTATING_VALIDATION_FAILURE`, preserve the namespace and all
immutable bytes, and stop publication without calling the scientific result
invalid. No second retry is permitted.

- Implementation defaults to eight local worker processes. Independent seed
  substreams plus final deterministic sorting must make all outputs invariant
  to worker completion order.
- Before calibration freeze, run `--phase runtime-benchmark --workers 8` using
  development/calibration payloads only. Benchmark each of the four nested
  scenarios at calibration `replicate_index = 0`. Benchmark
  `sparse_expected_failure` and each non-equal control or stress at development
  `replicate_index = 0`.
- The equal-emission timing unit is a timing-only development bundle of 24
  generated replicates with `replicate_index = 0, ..., 23`, plus one
  development bootstrap bundle with `component = bootstrap`,
  `draw_index = 0`, and pseudo-replicate `replicate_index = 0, ..., 23`. This
  runtime-benchmark-only exception does not expand the scientific development
  index range. It cannot construct a holdout payload and emits no scientific
  row.
- Time one complete task unit per scenario, including its required fit,
  profiles, and 199 predictive references where applicable. Separately time
  one complete equal-emission bootstrap-bundle refit.
- Build exact calibration and holdout task-duration lists by repeating each
  measured task-unit duration for its frozen task count. The equal-emission
  holdout list includes 199 copies of the measured bootstrap-bundle refit
  duration.
- Project each eight-worker makespan by deterministic longest-processing-time
  scheduling. Sort task durations descending, breaking ties by stable task ID;
  assign each task to the currently least-loaded worker, breaking load ties by
  lowest worker index. Set
  `projected_seconds = 1.20 * max(worker_loads)`.
- `runtime_projection.json` records every task ID, measured duration, repeated
  calibration and holdout count, exact expanded task-duration lists, both
  eight-element worker-load vectors, safety factor `1.20`, and both projected
  seconds. Require projected calibration and projected holdout makespans each
  at most `1500` seconds.

The runtime task-unit registry is literal, ordered by the frozen scenario
registry, and has these values:

| Scenario | `task_id` | Benchmark split/range | Calibration repeats | Holdout repeats | Profiles | Predictive references | Scientific row |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| `process_oracle_observed_transition` | `benchmark|scenario=process_oracle_observed_transition` | `calibration`, `0..0` | 24 | 48 | true | 0 | true |
| `observation_oracle_fixed_transition` | `benchmark|scenario=observation_oracle_fixed_transition` | `calibration`, `0..0` | 24 | 48 | true | 199 | true |
| `dense_count_exact_model` | `benchmark|scenario=dense_count_exact_model` | `calibration`, `0..0` | 24 | 48 | true | 199 | true |
| `structured_imperfect_effort` | `benchmark|scenario=structured_imperfect_effort` | `calibration`, `0..0` | 24 | 48 | true | 199 | true |
| `sparse_expected_failure` | `benchmark|scenario=sparse_expected_failure` | `development`, `0..0` | 0 | 24 | true | 199 | true |
| `zero_driver_effect_negative_control` | `benchmark|scenario=zero_driver_effect_negative_control` | `development`, `0..0` | 0 | 24 | true | 199 | true |
| `permuted_arrival_alignment_stress` | `benchmark|scenario=permuted_arrival_alignment_stress` | `development`, `0..0` | 0 | 24 | true | 199 | true |
| `no_emission_contrast_negative_control` | `benchmark|scenario=no_emission_contrast_negative_control` | `development`, `0..23` | 0 | 1 | false | 199 | false |
| `informative_dropout_misspecification_stress` | `benchmark|scenario=informative_dropout_misspecification_stress` | `development`, `0..0` | 0 | 24 | true | 199 | true |
| `goal018_continuous_abundance_stress` | `benchmark|scenario=goal018_continuous_abundance_stress` | `development`, `0..0` | 0 | 24 | true | 199 | true |
| `spatial_frailty_stress` | `benchmark|scenario=spatial_frailty_stress` | `development`, `0..0` | 0 | 24 | true | 199 | true |

The separate equal-emission bootstrap unit is exactly
`benchmark|scenario=no_emission_contrast_negative_control|component=bootstrap|bundle=0000`,
uses development bundle `0`, pseudo-replicates `0..23`, calibration repeats
`0`, holdout repeats `199`, and `scientific_row=false`. Calibration expansion
contains exactly 96 tasks. Its IDs are
`calibration|scenario=<scenario_id>|replicate=<0000..0023>` for the first four
scenarios in registry order. Holdout expansion contains exactly 536 tasks. For
each non-equal scenario in registry order its IDs are
`holdout|scenario=<scenario_id>|replicate=<zero-padded index>`; the equal shared
bundle ID is
`holdout|scenario=no_emission_contrast_negative_control|bundle=0000`, followed
immediately by bootstrap IDs
`holdout|scenario=no_emission_contrast_negative_control|component=bootstrap|draw=<0000..0198>`.
Every expanded duration equals its registered measured unit duration. The
arrays remain in this declared order before LPT assignment. `safety_factor` is
exactly `1.20`; each projection is exactly `1.20 * max(worker_loads)`; and
`passed` is true exactly when both projections are at most `1500`, both
pre-exposure counters are false, and every preceding reconstruction succeeds.
- The actual full calibration command must complete within 30 minutes before
  freeze, equivalently at most `1800` seconds. If the benchmark, projection, or
  calibration misses its gate, stop before holdout and return to Barry for a
  runtime/resource/scope decision. Do not reduce evidence, use remote compute,
  change thresholds, or expose holdout.

## Deterministic Gates

For every nested holdout coverage gate, the denominator is every attempted
holdout replicate for each applicable parameter, fixed at `n = 48`.
Nonconverged, nonfinite, open-profile, or missing intervals have
`truth_in_interval = false` rather than being excluded.

For median and maximum absolute error, a nonconverged or missing estimate is
imputed as that parameter's full natural support width. For interval-width
summaries, a nonconverged, open, or missing interval is imputed as full natural
support width. Use all 48 rows. Median signed error is descriptive over finite
converged estimates only and is nullable. Convergence fractions retain the
total attempted denominator.

The exact central binomial acceptance set for `Binomial(n, p)` at alpha is
computed by enumerating `k = 0, ..., n` and retaining `k` exactly when

```text
scipy.stats.binom.cdf(k, n, p) > alpha / 2
and
scipy.stats.binom.sf(k - 1, n, p) > alpha / 2.
```

The inclusive acceptance bounds are the minimum and maximum retained `k`.
Coverage uses `n = 48`, `p = 0.90`, and `alpha = 0.05 / 15`. The zero-driver
false-positive gate uses its full 24-attempt holdout denominator, `p = 0.10`,
and `alpha = 0.05`.

The `sparse_expected_failure` honest-coverage rule is separate from the 15
nested-family coverage gates. For `beta_driver`, its denominator is every one
of the `24` attempted holdout replicates. A nonconverged or nonfinite fit, an
open profile, or a missing interval has `truth_in_interval = false`, exactly as
in the nested rule. Construct its inclusive acceptance set with the same exact
central-binomial enumeration above using `n = 24`, `p = 0.90`, and
`alpha = 0.05`. The sparse coverage count must fall within that inclusive set.
Sparse inference is expected to be wider and weaker, but false exclusions may
not exceed this dedicated tolerance.

The sparse `beta_driver` median-width comparison also uses all 24 attempted
holdout replicates. A nonconverged fit, open interval, or missing interval is
imputed as the full `beta_driver` natural support width, `6`. Sort the resulting
24 widths and use the ordinary even-sample median, the arithmetic mean of the
12th and 13th one-based ordered values. Compare this sparse median with the
structured `beta_driver` median computed under its already-frozen 48-attempt
full-support-width imputation rule.

Claimed recovered estimands must also satisfy these parameter-specific holdout
limits:

| Parameter | Maximum median absolute error | Maximum median interval width |
| --- | ---: | ---: |
| `alpha` | `0.40` | `2.00` |
| `beta_driver` | `0.20` | `1.00` |
| `beta_quality` | `0.20` | `1.00` |
| `lambda_quasi` | `0.05` | `0.30` |
| `lambda_present` | `0.40` | `1.50` |

Additional gates:

- convergence fraction is at least `0.95` for both oracle gates and dense exact
  model, and at least `0.90` for structured imperfect effort;
- sparse `beta_driver` median interval width is at least that of structured
  effort, and its 24-attempt coverage count remains inside the dedicated exact
  binomial acceptance set;
- zero-driver intervals exclude zero no more often than the preregistered 10%
  false-positive tolerance;
- permuted-arrival heldout log score is worse than the correctly aligned model
  in at least 22 of 24 paired holdout replicates and at least one
  preregistered warning fires for the permuted fitted model on the fixed score
  cells; it is an alignment stress, not a null false-positive test;
- no-emission contrast passes the frozen 199-bootstrap rule and is classified
  unidentifiable;
- exact-model randomised PIT checks use Holm-adjusted familywise alpha `0.01`
  across preregistered overall and stratum checks;
- informative dropout, continuous abundance, and spatial frailty are stress
  diagnostics. Informative dropout and spatial frailty retain known generating
  parameters and must report coverage/bias. Continuous abundance has no
  parameter-recovery claim. Any stress that produces narrow wrong inference
  without a preregistered predictive warning is a
  `silent_misspecification_failure` and blocks a passing recommendation.

For informative-dropout and spatial-frailty stresses, `narrow wrong` means any
known parameter's 90% interval excludes truth while its width is no larger than
that parameter's frozen maximum above.

The equal-emission control uses dense schedule, effort `1`, and all 24 holdout
replicates. Its equal submodel has sole parameter `lambda_equal` with support
`[0.01, 10]` and shared MLE
`clip(sum(Y) / sum(E), 0.01, 10)`; its log likelihood is the direct Poisson sum.
The ordered alternative shares one five-parameter vector across all 24
replicates and maximises summed joint log likelihood with the frozen eight-start
optimizer; no profiles are computed. For bootstrap bundle `b`, generate all 24
equal-model pseudo-replicates with the frozen bootstrap mapping, refit both
models, and set `D_b = 2 * (LLordered - LLequal)`. Then

```text
p = (1 + count(D_b >= D_observed)) / 200.
```

Any failed ordered bundle fit makes the control fail; it is never excluded.
No profiles are computed for this control. Its scenario-specific statuses are
fixed independently of p:

| Parameter | Structural status | Practical status |
| --- | --- | --- |
| `alpha` | `unidentified` | `unidentified` |
| `beta_driver` | `unidentified` | `unidentified` |
| `beta_quality` | `unidentified` | `unidentified` |
| `lambda_quasi` | `unidentified` | `unidentified` |
| `lambda_present` | `identified` | `not_applicable` |
| `lambda_equal` | `identified` | `identified` subject to a finite interior MLE |

Known-present `t_0` emissions identify the `lambda_present` baseline level.
Equal emissions make the ordered `lambda_present/lambda_quasi` contrast
unidentifiable; they do not erase that baseline identification. The control
gate passes only when `p >= 0.05` and all 199 ordered bundle refits succeed. If
`p < 0.05` or any ordered bundle refit fails, the gate fails and the final
recommendation is `model_contract_failed`, but no bootstrap outcome changes
the structural labels. No profile-based override is permitted.

### Predictive applicability and fixed frames

- `process_oracle_observed_transition` has no counts and is excluded from
  predictive diagnostics.
- `observation_oracle_fixed_transition` receives oracle-only conditional
  predictive reporting with transitions held fixed. This reporting cannot
  satisfy or substitute for a joint predictive gate.
- Standard predictive gates are required for `dense_count_exact_model`,
  `structured_imperfect_effort`, `sparse_expected_failure`,
  `zero_driver_effect_negative_control`,
  `permuted_arrival_alignment_stress`,
  `informative_dropout_misspecification_stress`,
  `goal018_continuous_abundance_stress`, and `spatial_frailty_stress`.
- `no_emission_contrast_negative_control` generates predictive references from
  its fitted equal submodel. Its standard predictive warning is diagnostic
  only; the 199-bundle bootstrap above is the exact classification rule.

For every predictive-applicable scenario, observed and reference metrics use
exactly the retained fitting/evaluation opportunity frame, with cell, time,
effort, and dropout mask fixed. Reference datasets never add, remove, or alter
an opportunity, schedule, effort value, or dropout decision. For
`permuted_arrival_alignment_stress`, the primary predictive reference is the
permuted fitted model evaluated on the fixed score cells; this is the model
required to fire at least one warning. The correct-alignment fit is a heldout
score comparator only and is not a substitute predictive reference.

One module-issued `PredictiveOpportunityFrameEvidence` is adapted from the
actual canonical `ScheduledOpportunity` tuple consumed for that replicate. The
adapter rejects any schedule size, cell identity, time, exact effort, or cell
covariate difference. Its canonical ASCII serialization starts with scenario,
split, replicate, and `fit|score` role, then emits every opportunity in sorted
cell/time order as:

```text
cell_id=<int>|time=<int>|effort_hex=<float.hex()>|quality_stratum=<q1..q5>|time_band=<early|middle|late>|keep_key=cell_id=<int>|time=<int>|kept=<0|1>
```

The opportunity SHA-256 covers that complete serialization, including dropped
rows and keyed keep state. Informative dropout additionally hashes each
`keep_key|kept` entry in the same canonical order; positional mask bits are not
an authority. Quality labels and time bands derive from the canonical source
frame and model time. Thus equal-cardinality quality or time-band swaps, one
effort mutation, or a keyed keep/drop swap changes evidence or is rejected.
Counts, all nine stratum memberships, and all three metrics per stratum are
computed from the retained opportunity objects in this issued frame. No
parallel fixture metadata may supply sample size or digest.

Predictive strata are frozen in this order:

1. `all`;
2. quality quintiles `q1, q2, q3, q4, q5`; and
3. time bands `early` (`t = 0, ..., 36`), `middle` (`t = 42, ..., 78`), and
   `late` (`t = 84, ..., 120`).

Within each stratum, metric order is `mean_count`, `zero_fraction`, then
`variance_to_mean`. These nine strata by three metrics define 27 stable
stratum-metric cells.

For stratum counts `y_1, ..., y_n`, metrics are literal:

```text
mean_count = sum(y_i) / n
zero_fraction = count(y_i = 0) / n
variance_to_mean = sample_variance(y, ddof=1) / mean_count
                   when n >= 2 and mean_count > 0
variance_to_mean = 0 when n >= 2 and mean_count = 0.
```

When `mean_count = 0`, nonnegative counts imply all values are zero. Any
stratum with `n < 2` is invalid and makes the scenario predictive gate fail.

Predictive diagnostics require every scenario-specific required fit to be
successful and finite. A failed or nonfinite required fit prevents predictive
diagnostics for that attempted replicate, creates no substitute reference
ensemble, and makes the scenario predictive gate fail. The attempted replicate
remains in every predictive denominator and is emitted as diagnostically
unavailable; it is never silently omitted. Available-fit diagnostics may be
reported descriptively but cannot rescue the failed scenario gate.

Each fitted replicate generates one 199-dataset predictive-reference ensemble,
reused across all strata. For each replicate/stratum/metric, record observed
value, reference mean, reference sample SD with `ddof=1`,
`reference_mcse = reference_sd / sqrt(199)`, and
`standardized_residual = (observed - reference_mean) / reference_sd`. If
reference SD is zero, the standardized residual is zero only when observed
equals reference mean; otherwise it is signed infinity.

Randomized rank PIT is

```text
u = (L + V * (E_tie + 1)) / 200,
```

where `L` is the number of references below observed, `E_tie` is the number
equal to observed, and `V` is consumed from the replicate's
`pit_randomization` generator in frozen stratum then metric order.

For each scenario/split and each of the 27 cells, apply
`scipy.stats.kstest(replica_pit_values, "uniform", method="exact")`. Holm-adjust
all 27 raw p-values by sorting on p-value then the stable cell key
`(stratum_order, metric_order)` from the frozen orders above. At sorted
one-based position `i`, set

```text
holm_adjusted_p_i = min(1, max_{j <= i}((27 - j + 1) * p_j)),
```

then map back to cell order. Reject when adjusted p is below `0.01`.

For each cell, pool finite replicate standardized residuals with
`stouffer_z = sum(z) / sqrt(n_valid)`. Any nonfinite standardized residual
produces a warning. A warning also fires when Holm-adjusted PIT p is below
`0.01` or `abs(stouffer_z) > 3`. MCSE is retained only as predictive-reference
accuracy reporting and is never a warning threshold. The continuous-abundance
stress must warn; a narrow-wrong stress without warning remains a
`silent_misspecification_failure`.

The summary `replicate_count` is the full number of attempted replicates for
that scenario/split/cell. `mean_standardized_residual` is the mean over the
same `n_valid` finite residuals used by Stouffer and is empty when
`n_valid = 0`; the attempted count is never reduced by a nonfinite residual or
failed fit.
When any attempted fit failed or was nonfinite, `diagnostic_count` is smaller
than `replicate_count`, inferential summary statistics may be empty, and the
summary has `warning = true` and `gate_result = fail`.

Because artifacts cannot emit NaN or infinity, a nonfinite replicate
standardized residual is serialized as an empty structurally nullable value
with `standardized_residual_nonfinite = true`; the warning remains mandatory.
Likewise a nonfinite or undefined aggregate Stouffer Z is serialized empty and
forces `warning = true`.

## Recommendation Precedence

Preserve exactly these four classes and ranks:

1. `model_contract_failed`
2. `process_observation_confounded`
3. `observation_limited_but_calibrated`
4. `latent_response_observation_gate_passed`

Compute every applicable local reducer so all reasons remain visible, then use:

```text
required_control_ids = {
    zero_driver_effect_negative_control,
    no_emission_contrast_negative_control,
}

required_stress_ids = {
    permuted_arrival_alignment_stress,
    informative_dropout_misspecification_stress,
    goal018_continuous_abundance_stress,
    spatial_frailty_stress,
}

contract_failure =
    any frozen source/schema/analytic/likelihood/holdout/artifact/provenance/
        numerical-domain/potential-design/noncollision gate fails
    or any required input is missing, unknown, duplicate, contradictory,
        malformed, or unevaluated
    or any scenario reducer returns contract_failure

confounding = any scenario reducer returns confounding

structured_limitation =
    scenario 3 returns pass
    and scenario 4 returns structured_limitation
    and every scenario other than 4 returns pass

all_required_pass =
    every global contract gate passes
    and scenarios 1..11 each return pass
    and every required control and stress ID is present exactly once

if contract_failure:
    recommendation_rank = 1
    recommendation_class = model_contract_failed
elif confounding:
    recommendation_rank = 2
    recommendation_class = process_observation_confounded
elif structured_limitation:
    recommendation_rank = 3
    recommendation_class = observation_limited_but_calibrated
elif all_required_pass:
    recommendation_rank = 4
    recommendation_class = latent_response_observation_gate_passed
else:
    recommendation_rank = 1
    recommendation_class = model_contract_failed
    reason = incomplete_or_contradictory_decision_vector
```

Rank 3 is reachable only when every non-structured global/scenario gate,
including sparse honesty, both controls, and all four stresses, passes. Rank 4
is unreachable when any control or stress is absent, unavailable, invalid, or
fails its local rule. A valid arrival-alignment discrimination failure is rank
2; invalid or unavailable alignment is rank 1. Dropout and frailty warnings are
conditional on `narrow_wrong`; continuous abundance and valid alignment always
require at least one available scientific warning.

When several reasons occur, emit all reason flags in canonical global-gate then
scenario order. Choose the smallest recommendation rank. Within that rank, the
first canonical reason is primary. Unknown or contradictory vectors never
default to pass.

Always emit:

```text
transportability_class = scheduled_count_only_point_process_bridge_required
```

Latent-transition diagnostics are recommendation-neutral and excluded from the
state machine.

## Source And Artifact Contracts

`source_provenance.json` must contain schema version, source commit, selected
Goal 018 parameter-set ID, source API names, expected/reconciled headline
counts, and SHA-256 hashes of canonical landscape rows and the ordered `TP(x)`
vector.

Canonical source serialization is UTF-8 with LF endings, one header row, and
rows sorted by integer `cell_id`. Landscape columns are
`cell_id,row,col,passability,habitat_class,quality`; `TP(x)` columns are
`cell_id,predator_arrival_time`. Floats use Python `format(value, ".12g")`;
nonfinite arrival is the empty field; CSV quoting follows `csv.writer` with
`lineterminator="\n"`. Task 0 independently computes both SHA-256 values twice,
records the agreed values and method in the tracked
`source_digest_receipt.json`, and freezes that receipt before implementation.

Generated bundle:

```text
artifacts/synth_medium_latent_response_observation_recovery/
```

### Schema And Evidence Amendment

#### `scenario_definitions.csv`

Append these fields to the existing header:

```text
fit_scope,primary_fit_variant,comparator_fit_variant
```

Complete schema:

```text
scenario_id:str!
scenario_role:enum!
generation_model:enum!
fit_model:enum!
schedule_id:enum!
effort_rule:str!
development_replicates:int!
calibration_replicates:int!
holdout_replicates:int!
expected_behavior:enum!
truth_access_class:enum!
transportability_class:enum!
fit_scope:enum!
primary_fit_variant:enum!
comparator_fit_variant:enum?
```

Primary key: `scenario_id`.

Rows use the numbered scenario order in section 4, an explicit exception to
the general lexical primary-key sort rule.

#### `fit_execution_evidence.csv`

Add this root artifact with literal header:

```text
scenario_id,split_id,fit_scope,fit_variant,fit_index,source_replicate_first,source_replicate_last,source_replicate_count,fit_succeeded,converged_start_count,best_start_index,best_two_log_likelihoods_agree,at_boundary,boundary_parameter_ids,alpha_estimate,beta_driver_estimate,beta_quality_estimate,lambda_quasi_estimate,lambda_present_estimate,lambda_equal_estimate,log_likelihood,heldout_log_score,fit_failure_class,failure_code,evidence_row_type,design_kind,design_provenance,design_role,design_n_rows,design_n_columns,design_rank,design_condition_number,design_passed,design_failure_code,design_frame_cell_count,design_frame_sha256
```

Literal schema:

```text
scenario_id:str!
split_id:enum!
fit_scope:enum!
fit_variant:enum!
fit_index:int!
source_replicate_first:int!
source_replicate_last:int!
source_replicate_count:int!
fit_succeeded:bool?
converged_start_count:int?
best_start_index:int?
best_two_log_likelihoods_agree:bool?
at_boundary:bool?
boundary_parameter_ids:str?
alpha_estimate:float?
beta_driver_estimate:float?
beta_quality_estimate:float?
lambda_quasi_estimate:float?
lambda_present_estimate:float?
lambda_equal_estimate:float?
log_likelihood:float?
heldout_log_score:float?
fit_failure_class:enum?
failure_code:str?
evidence_row_type:enum!
design_kind:enum?
design_provenance:str?
design_role:str?
design_n_rows:int?
design_n_columns:int?
design_rank:int?
design_condition_number:float?
design_passed:bool?
design_failure_code:str?
design_frame_cell_count:int?
design_frame_sha256:str?
```

Primary key and sort key:

```text
(scenario_id,split_id,fit_scope,fit_variant,fit_index,evidence_row_type,design_kind)
```

The five fit-identity components sort lexically with numeric `fit_index`, then
`evidence_row_type` sorts `fit_result` before `design_diagnostic`, and design
kind sorts `potential`, `oracle`, `plugin`; the fit-result `design_kind` is
null and sorts before design kinds. Duplicate keys are forbidden. Row rules
are exact:

- Every fit identity emits exactly one `fit_result` row. Its sixteen fields
  from `fit_succeeded` through `failure_code` follow the fit-state rules below;
  all eleven design fields are null.
- Every required design identity emits one `design_diagnostic` row. Its fit
  fields from `fit_succeeded` through `failure_code` are null and all nine
  design fields are populated subject to the design-state rules below.
- Required design kinds are literal: process oracle has `potential,oracle`;
  observation oracle and `equal_rate` have `potential`; every other registered
  variant has `potential,plugin`. The complete frame therefore has exactly
  `990` fit-result rows and `1695` design-diagnostic rows.
- Potential and plug-in provenance/role are exactly
  `potential_design`/`ANALYST-PREFLIGHT` and
  `joint_plugin_smoothed_at_risk`/`ANALYST-JOINT-PRACTICAL`. Oracle provenance/
  role is exactly `process_oracle_truth_at_risk`/`ORACLE-BENCHMARK-ONLY`.
- Every design has `design_n_columns=3`. Potential and plug-in row counts are
  exactly `104500`, except sparse rows are exactly `26120` and arrival rows are
  exactly `83600 = 4180 * 20`; an oracle row count is the actual positive
  truth-at-risk count and cannot exceed its potential frame.
- `design_frame_cell_count` and `design_frame_sha256` bind every diagnostic to
  the sorted canonical cell IDs. For joint variants these fields are derived
  only from the module-issued frame carried by the validated `JointFitResult`;
  caller-populated constants are not an authority. Arrival potential and
  plug-in diagnostics bind only the exact 4180 fit-cell IDs and exactly 83600
  rows. A one-cell fit/score swap, score-history fit, or a 104500-row arrival
  diagnostic is invalid before potential construction or reduction. The 1045
  score cells are used only for heldout scoring and predictive comparison.
- `design_passed=true` exactly when `n_rows >= n_columns`, rank is `3`,
  condition is finite and at least `1`, and condition is strictly below
  `1e8`. Exactly `1e8` fails; the next representable value below passes. Rank
  is an exact integer in `0..min(n_rows,n_columns)`. Rank-deficient or
  unavailable/nonfinite condition is serialized null, never NaN or infinity.
- A passing design has null failure. A failed design has one typed code from
  `rank_deficient`, `condition_limit_failed`,
  `joint_fit_failed_or_nonfinite`, `not_evaluated_potential_failed`, or
  `process_oracle_fit_failed_or_nonfinite` with state-consistent rank and
  condition nullability.
- After exact identity partitioning, each fit identity follows the closed
  failure-class transition table below. `preflight_or_input_failure` is typed
  in memory but is never persistable because Task 3 starts only after the
  complete preflight. Potential-gate failure forbids every optimizer-result
  field. Plug-in-gate failure requires a successful multistart result. Rank or
  condition diagnostics are legal only with their matching design-gate class.

```text
potential_rank_gate_failure      -> potential rank_deficient; downstream not_evaluated_potential_failed
potential_condition_gate_failure -> potential condition_limit_failed; downstream not_evaluated_potential_failed
optimizer_or_nonfinite_failure   -> potential pass; joint/process downstream rank zero with its fit_failed_or_nonfinite code
plugin_rank_gate_failure         -> potential pass; plugin rank_deficient
plugin_condition_gate_failure    -> potential pass; plugin condition_limit_failed
oracle_rank_gate_failure         -> potential pass; oracle rank_deficient
oracle_condition_gate_failure    -> potential pass; oracle condition_limit_failed
equal_rate_noninterior_failure   -> potential pass; no downstream design
success                          -> every applicable design passes
```

  Observation-oracle optimizer failure is the potential-only applicability
  exception. Equal-rate remains potential-only. Every failed fit is
  parameter-null. Contradictions are rejected before any scenario, control,
  recommendation, or verification reduction.

- `fit_scope=replicate`: `fit_index`, `source_replicate_first`, and
  `source_replicate_last` all equal the scientific `replicate_id`; source count
  is `1`.
- `fit_scope=scenario_shared`: `fit_index=0`; equal-emission development uses
  source range `0..11`, count `12`; holdout uses `0..23`, count `24`.
- `fit_scope=bootstrap_shared`: only equal emission is legal;
  `fit_index=bundle_id` in `0..198`, source range `0..23`, count `24`.
- Timing-only equal-emission and timing-only bootstrap units emit no row because
  `scientific_row=false`.
- Every required attempt emits one fit-result row whether successful or failed.
  A failed row requires one applicable `fit_failure_class` and a nonempty
  `failure_code`; accepted estimates, likelihood, and heldout score are null.
  A successful row has null failure class and code.
- Multistart `fit_succeeded=true` requires at least six successful starts,
  finite accepted output, and best-two agreement. `converged_start_count` is
  `0..8`; `best_start_index`, when present, is `1..8`.
- The closed-form equal-rate fit has null start fields. A clipped boundary MLE
  is visible but has `fit_succeeded=false` and
  `fit_failure_class=equal_rate_noninterior_failure` plus
  `failure_code=equal_rate_mle_noninterior`.
- `boundary_parameter_ids` is null when no accepted parameter is on a boundary;
  otherwise it is a no-space `|`-joined list in frozen parameter order.
- Process oracle populates three process estimates; observation oracle two rate
  estimates; ordinary ordered fits five estimates; equal-rate fits only
  `lambda_equal_estimate`.
- Arrival emits correct and permuted replicate rows. Both fit on 4,180 cells and
  both heldout scores use only the 1,045 score cells. A paired win requires two
  successful finite rows and strict `correct > permuted` score.
- Equal emission emits two observed shared rows and two bootstrap-shared rows
  for every bundle. The paired likelihoods must exactly reproduce observed
  `D`, every `D_b`, and add-one p. All 199 ordered bootstrap rows must succeed.

This table is the sole fit-execution and convergence authority. Every fit-
derived science row must reconcile to exactly one permitted primary fit row.
`report.md` links this table directly. `control_comparison.svg` reads arrival
pair availability/scores and equal-emission observed/bootstrap fit evidence
back from this emitted table; live fit objects are not an alternative input.

#### Complete Literal Model And Fit-Derived Schemas

The schemas below are self-contained authority. `!` means required and
non-null; `?` means structurally nullable only under the row rules stated
below. An `int` never accepts a boolean. Every populated `float` is finite.
Empty strings are not substitutes for required values, and no CSV may contain
NaN or infinity.

Literal enum domains shared by these tables are:

```text
scenario_id = process_oracle_observed_transition|observation_oracle_fixed_transition|dense_count_exact_model|structured_imperfect_effort|sparse_expected_failure|zero_driver_effect_negative_control|permuted_arrival_alignment_stress|no_emission_contrast_negative_control|informative_dropout_misspecification_stress|goal018_continuous_abundance_stress|spatial_frailty_stress
split_id = development|calibration|holdout
fit_variant = canonical|correct_alignment|permuted_alignment|equal_rate|ordered_emission
parameter_id = alpha|beta_driver|beta_quality|lambda_quasi|lambda_present|lambda_equal
structural_status = identified|unidentified|not_applicable
practical_status = identified|unidentified|not_applicable
gate_result = pass|fail|diagnostic|warning|not_applicable
latent_metric_id = transition_brier|transition_interval_score|transition_median_absolute_error
predictive_metric_id = mean_count|zero_fraction|variance_to_mean
stratum_type = all|habitat_quality_quintile|time_band
stratum_value = all|q1|q2|q3|q4|q5|early|middle|late
```

`stratum_type,stratum_value` combinations are restricted to the frozen nine
strata. `lambda_equal` occurs only in equal-emission fit/status evidence. A
model-parameter row uses only the first five parameter IDs.

`model_parameter_contract.csv` has literal header:

```text
parameter_id,role,units,transform,lower_bound,upper_bound,generating_value,fitted_scenarios,structural_status,practical_status,interpretation
```

Its literal schema is:

```text
parameter_id:enum!
role:enum(baseline_cloglog_hazard_intercept|scaled_time_since_arrival_effect|standardized_habitat_quality_effect|quasi_extirpated_effective_count_rate|present_effective_count_rate)!
units:enum(log_hazard|log_hazard_per_scaled_time|log_hazard_per_quality_sd|counts_per_effort)!
transform:enum(identity_natural_space|ordered_rate_natural_space)!
lower_bound:float!
upper_bound:float!
generating_value:float!
fitted_scenarios:str!
structural_status:enum!
practical_status:enum!
interpretation:str!
```

Primary key is `(parameter_id)`. Sort in frozen parameter order `alpha`,
`beta_driver`, `beta_quality`, `lambda_quasi`, `lambda_present`.
`fitted_scenarios` is a no-space `|`-join in frozen scenario order.
`structural_status` reports whether the accepted model/evidence identifies the
parameter; `practical_status` reports the finite two-sided-profile rule and is
`not_applicable` only when the contract computes no profile. Config parameter
items are exactly this row without `structural_status` and
`practical_status`.

`replicate_recovery.csv` has literal header and schema:

```text
scenario_id,split_id,replicate_id,fit_variant,parameter_id,truth_value,estimate,interval_lower,interval_upper,interval_width,converged,converged_start_count,at_boundary,profile_two_sided,truth_in_interval,log_likelihood,signed_error,absolute_error,gate_result

scenario_id:enum!
split_id:enum!
replicate_id:int!
fit_variant:enum!
parameter_id:enum!
truth_value:float?
estimate:float?
interval_lower:float?
interval_upper:float?
interval_width:float?
converged:bool!
converged_start_count:int?
at_boundary:bool?
profile_two_sided:bool!
truth_in_interval:bool?
log_likelihood:float?
signed_error:float?
absolute_error:float?
gate_result:enum!
```

Primary/sort key is
`(scenario_id,split_id,replicate_id,fit_variant,parameter_id)`, with string
components lexical and integers numeric. Failed fits have `converged=false`,
null accepted estimate/likelihood/boundary fields, null interval fields, and
`profile_two_sided=false`. `truth_value`, `truth_in_interval`, and errors are
nullable only where the stress has no parameter-truth claim or the fit/profile
is unavailable. For a finite two-sided interval, width equals upper minus
lower, `truth_in_interval` is inclusive, signed error is estimate minus truth,
and absolute error is its absolute value. The zero-driver decision reads these
canonical emitted rows: exactly the 24 sorted holdout `beta_driver` rows,
reconciled one-to-one to successful/failed canonical fit evidence. No private
substitute interval table or caller-nominated interval vector is authoritative.

`coverage_calibration.csv` has literal header and schema:

```text
scenario_id,split_id,fit_variant,parameter_id,replicate_count,converged_count,coverage_count,coverage_fraction,acceptance_lower_count,acceptance_upper_count,median_signed_error,median_absolute_error,median_interval_width,maximum_absolute_error,maximum_interval_width,gate_result

scenario_id:enum!
split_id:enum!
fit_variant:enum!
parameter_id:enum!
replicate_count:int!
converged_count:int!
coverage_count:int!
coverage_fraction:float!
acceptance_lower_count:int?
acceptance_upper_count:int?
median_signed_error:float?
median_absolute_error:float?
median_interval_width:float?
maximum_absolute_error:float?
maximum_interval_width:float?
gate_result:enum!
```

Primary/sort key is `(scenario_id,split_id,fit_variant,parameter_id)`.
Counts use the complete attempted frame and satisfy
`coverage_fraction=coverage_count/replicate_count`. Acceptance counts are
structurally nullable only for descriptive stress rows. A median is nullable
only when its declared finite contributing set is empty.

`latent_time_calibration.csv` has literal header and schema:

```text
scenario_id,split_id,replicate_id,fit_variant,metric_id,sample_size,fit_succeeded,diagnostic_available,observed_value,expected_value,error,gate_result

scenario_id:enum!
split_id:enum!
replicate_id:int!
fit_variant:enum!
metric_id:latent_metric_id!
sample_size:int!
fit_succeeded:bool?
diagnostic_available:bool!
observed_value:float?
expected_value:float?
error:float?
gate_result:enum!
```

Primary/sort key is
`(scenario_id,split_id,replicate_id,fit_variant,metric_id)`. Applicable rows
have typed `fit_succeeded`; available rows have all three finite metric values.
Unavailable applicable rows have those values null. Inapplicable rows have
`fit_succeeded=null`, `sample_size=0`, null values, and
`gate_result=not_applicable`.

`predictive_replicate_diagnostics.csv` has literal header and schema:

```text
scenario_id,split_id,replicate_id,fit_variant,stratum_type,stratum_value,metric_id,sample_size,opportunity_frame_count,opportunity_frame_sha256,dropout_mask_sha256,fit_succeeded,diagnostic_available,observed_value,reference_mean,reference_sd,reference_mcse,standardized_residual,standardized_residual_nonfinite,randomized_pit

scenario_id:enum!
split_id:enum!
replicate_id:int!
fit_variant:enum!
stratum_type:enum!
stratum_value:enum!
metric_id:predictive_metric_id!
sample_size:int!
opportunity_frame_count:int!
opportunity_frame_sha256:str!
dropout_mask_sha256:str?
fit_succeeded:bool!
diagnostic_available:bool!
observed_value:float?
reference_mean:float?
reference_sd:float?
reference_mcse:float?
standardized_residual:float?
standardized_residual_nonfinite:bool!
randomized_pit:float?
```

Primary/sort key is
`(scenario_id,split_id,replicate_id,fit_variant,stratum_type,stratum_value,metric_id)`
in frozen stratum then metric order. Each replicate emits exactly 27 rows.
Every row repeats the exact retained opportunity-frame count and SHA-256. The
dropout-mask SHA-256 is populated only for informative dropout and binds its
realized fixed mask; it is null otherwise. Arrival binds the exact score-cell
frame, while every other scenario binds its declared fitting/evaluation frame.
The three metrics within a stratum carry one identical `sample_size`, derived
from the same retained objects consumed by metric calculation rather than
supplied by a caller. The existing count/digest/mask columns are the persisted
evidence inside the unchanged 22-artifact registry. Any count, semantic digest,
metric-specific size, fit/score-frame, effort, stratum, or keyed-mask mismatch
is invalid before predictive summary, recommendation, or verification.
Available rows require a successful fit, finite observed/reference values,
nonnegative SD, `reference_mcse=reference_sd/sqrt(199)`, and PIT in `[0,1]`.
Count means and variance-to-mean are nonnegative; zero fractions are in
`[0,1]`. A zero SD with unequal observed/reference values is the specified
available nonfinite state: `standardized_residual` is structurally nullable,
the nonfinite flag is true, and downstream warning is mandatory. A zero SD
with equal values has residual zero and a false flag. Failed-fit unavailable
rows have all six diagnostic values null and a false nonfinite flag.

`predictive_check_summary.csv` has literal header and schema:

```text
scenario_id,split_id,fit_variant,stratum_type,stratum_value,metric_id,replicate_count,diagnostic_count,failed_fit_count,mean_standardized_residual,stouffer_z,ks_statistic,raw_p,holm_adjusted_p,warning,gate_result

scenario_id:enum!
split_id:enum!
fit_variant:enum!
stratum_type:enum!
stratum_value:enum!
metric_id:predictive_metric_id!
replicate_count:int!
diagnostic_count:int!
failed_fit_count:int!
mean_standardized_residual:float?
stouffer_z:float?
ks_statistic:float?
raw_p:float?
holm_adjusted_p:float?
warning:bool!
gate_result:enum!
```

Primary/sort key is
`(scenario_id,split_id,fit_variant,stratum_type,stratum_value,metric_id)`.
Counts reconcile to the complete attempted replicate frame. P-values and KS
statistics, when populated, are in `[0,1]`. Any failed/unavailable replicate,
nonfinite residual, or nonfinite aggregate requires `warning=true`; required
predictive gates then use `gate_result=fail`. Nullable aggregate fields never
reduce the attempted denominator.

`identifiability_profiles.csv` has literal header and schema:

```text
scenario_id,split_id,replicate_id,fit_variant,parameter_id,grid_index,parameter_value,profile_log_likelihood,likelihood_ratio_delta,nuisance_converged,inside_interval

scenario_id:enum!
split_id:enum!
replicate_id:int!
fit_variant:enum!
parameter_id:enum!
grid_index:int!
parameter_value:float!
profile_log_likelihood:float?
likelihood_ratio_delta:float?
nuisance_converged:bool!
inside_interval:bool?
```

Primary/sort key is
`(scenario_id,split_id,replicate_id,fit_variant,parameter_id,grid_index)`.
Grid indices are contiguous in deterministic profile order. A failed nuisance
fit has null profile likelihood, delta, and interval membership. A successful
point has finite likelihood/delta and typed membership; delta reproduces the
frozen likelihood-ratio algebra.

For every successful primary replicate fit and every parameter fitted by that
scenario, the profile table contains one complete group. The group contains the
unique MLE point and, on each side, either a closed crossing or an explicitly
open support-bound point. A closed side contains the inward and outward
sign-changing bracket points plus exactly one emitted Brent root point whose
absolute LR-delta difference from `2.705543454095404` is at most
`1e-8 * (1 + 2.705543454095404)`. An open side reaches its literal natural
support bound without a sign-changing bracket; a failed or omitted interior
point alone cannot nominate an endpoint. The reconstructed endpoint is the
root point's parameter value for a closed side and null for an open side.
`profile_two_sided` is true exactly when both endpoints are finite. Recovery
`interval_lower`, `interval_upper`, `interval_width`, `truth_in_interval`,
signed/absolute errors, and row gate are recomputed from this profile and its
one fit row; caller-provided derived values have no authority.

The complete science-bundle validator consumes fit execution, recovery,
profiles, coverage, latent diagnostics, predictive replicate diagnostics and
their summary, and control decisions. It derives the complete
scenario/split/primary-variant frame from `scenario_definitions`: all scenarios
have development and holdout; only the first four nested scenarios have
calibration; every replicate-scoped scenario has every numeric replicate
identity; arrival additionally has its comparator fit only; and equal emission
has only its shared observed pairs and 199 holdout bootstrap pairs.
Recovery/profile/coverage parameter subsets, latent applicability, and
predictive applicability are then derived from the literal registries. Missing,
extra, duplicate, reordered, foreign-split, foreign-variant, or orphan groups
fail before any gate is evaluated.

General rows use `canonical`; arrival primary rows use
`permuted_alignment`; equal-emission predictive rows use `equal_rate`. Equal
emission has no recovery, coverage, latent-time, or profile rows. Arrival's
`correct_alignment` comparator has no recovery, coverage, latent-time,
profile, or predictive row.

#### Descriptive Stress Recovery

Arrival, informative dropout, continuous abundance, and spatial frailty retain
all attempted primary-fit parameter rows. They cannot silently become new
recovery gates.

For arrival, informative dropout, and spatial frailty:

- emit five `replicate_recovery` rows per attempted primary fit;
- retain generating values only in evaluator-side row construction;
- failed/nonfinite fits retain rows with null accepted estimate/interval fields;
- failed/open/missing intervals are uncovered in the full attempted
  denominator;
- descriptive median/maximum absolute error and interval width use the same
  full-support imputations as nested rows;
- median signed error uses finite converged estimates only and is nullable;
- coverage denominators are `12` development and `24` holdout;
  `acceptance_lower_count` and `acceptance_upper_count` are null; and
- recovery/coverage `gate_result` is `diagnostic` with complete fit evidence
  and `warning` when required fit/profile evidence is unavailable. This field
  never overrides the separate required-fit or predictive reducer.

For continuous abundance:

- emit five primary-fit recovery rows per attempt for estimates, intervals,
  convergence, boundaries, and likelihood;
- `truth_value`, `truth_in_interval`, `signed_error`, and `absolute_error` are
  null;
- emit one coverage row per parameter with attempted/converged counts and
  descriptively imputed interval-width summaries;
- coverage counts/fractions/bounds and signed/absolute-error summaries are
  null; and
- use the same diagnostic/warning availability convention.

#### Control Summary

Replace the `control_decision_summary.csv` header with:

```text
decision_row_id,decision_row_type,scenario_id,parameter_id,structural_status,practical_status,gate_family,gate_result,test_statistic,bootstrap_replicates,bootstrap_converged_count,bootstrap_failed_count,p_value,alignment_correlation,silent_misspecification_failure,attempted_replicates,evaluable_replicates,event_count,acceptance_lower_count,acceptance_upper_count,recommendation_rank,recommendation_class,transportability_class,interpretation
```

Primary key and row sort: `decision_row_id`, lexical.

```text
decision_row_type = scenario_gate|parameter_status|final_decision
scenario_gate ID = scenario_gate|<scenario_id>
parameter status ID = parameter_status|no_emission_contrast_negative_control|<parameter_id>
final ID = final_decision
```

Add nullable fields:

```text
attempted_replicates:int?
evaluable_replicates:int?
event_count:int?
acceptance_lower_count:int?
acceptance_upper_count:int?
bootstrap_converged_count:int?
bootstrap_failed_count:int?
```

The complete schema is:

```text
decision_row_id:str!
decision_row_type:enum!
scenario_id:str?
parameter_id:str?
structural_status:enum?
practical_status:enum?
gate_family:enum!
gate_result:enum!
test_statistic:float?
bootstrap_replicates:int?
bootstrap_converged_count:int?
bootstrap_failed_count:int?
p_value:float?
alignment_correlation:float?
silent_misspecification_failure:bool!
attempted_replicates:int?
evaluable_replicates:int?
event_count:int?
acceptance_lower_count:int?
acceptance_upper_count:int?
recommendation_rank:int?
recommendation_class:enum?
transportability_class:enum!
interpretation:str!
```

Equal emission records attempted `24`; evaluable `24` only when both observed
shared fits are valid, otherwise `0`; observed `D`; bootstrap count `199`;
successful ordered-refit count; failed count `199-successful`; and p only when
all required statistics are finite. All values must recompute from
`fit_execution_evidence.csv`.

Zero driver records attempted `24`; evaluable only for successful finite fits
with finite closed two-sided `beta_driver` intervals; event count as intervals
excluding zero; and bounds `0..6`. Any evaluable count below `24` is an
availability failure, not a non-exclusion or denominator reduction.

Arrival records attempted `24`; evaluable as complete finite fit pairs; event
count as strict correct-score wins; and bounds `22..24`. Any evaluable count
below `24` is an availability failure.

#### Enum Additions

Keep every existing enum and add:

```text
fit_scope = replicate|scenario_shared|bootstrap_shared
fit_variant = canonical|correct_alignment|permuted_alignment|equal_rate|ordered_emission
decision_row_type = scenario_gate|parameter_status|final_decision
```

`bootstrap_shared` occurs only in fit evidence. Do not add a latent threshold
enum, fifth recommendation, sentinel fit ID, nullable primary-key component,
or JSON hidden in an interpretation field.

### Artifact Set And Hash Interfaces

#### Exact 22-File Bundle

Replace the current 21-file expected set with this literal 22-file order:

```text
recovery_gate_config.json
runtime_projection.json
source_provenance.json
holdout_manifest.json
model_parameter_contract.csv
scenario_definitions.csv
fit_execution_evidence.csv
replicate_recovery.csv
coverage_calibration.csv
latent_time_calibration.csv
predictive_replicate_diagnostics.csv
predictive_check_summary.csv
identifiability_profiles.csv
control_decision_summary.csv
verification.json
report.md
visuals/parameter_recovery.svg
visuals/coverage_calibration.svg
visuals/latent_time_calibration.svg
visuals/identifiability_profiles.svg
visuals/control_comparison.svg
visuals/review_montage.svg
```

The config `artifact_manifest` is an expected-set registry, not a final
integrity manifest. It has exactly 22 entries in that order. Every entry has
exactly `path`, `role`, `required`, and `sha256`; every `required=true`; every
`sha256=null`. The config is immutable after self-hashing.

The artifact-manifest document is `verification.json`. Freeze
`checks[name="artifact_manifest"].details` to exactly:

```text
schema_version:str
entries:list[{path:str,sha256:str}]
represented_artifact_set_sha256:str
```

Its `entries` list contains the other 21 files exactly once in the literal
bundle order, with `verification.json` omitted. Compute
`represented_artifact_set_sha256` over UTF-8 lines:

```text
<file_sha256><two spaces><relative_artifact_path>\n
```

in represented-entry order. Missing, extra, duplicate, zero-byte, nonregular,
or changed files fail verification.

Every verification check has exactly `name`, `passed`, and `details`. For each
of the eleven scenario gate families, `details` is exactly
`{decision_row_id,gate_result,reason}` and binds the corresponding recomputed
scenario row. `parameter_status.details` is exactly
`{decision_row_ids,status_rows_sha256}` for the six literal status rows.
`final_recommendation.details` is exactly
`{decision_row_id,recommendation_rank,recommendation_class,reason,transportability_class}`.
`artifact_manifest.details` is the exact three-key manifest object above.
`tracked_state.details` is exactly
`{tracked_state_sha256,runtime_projection_passed,source_provenance_passed,holdout_manifest_exposed}`.
The verification spec/config/source hashes equal the validated config and
holdout bindings. Check booleans are derived from those validated objects;
recommendation and transportability equal the recomputed final control row;
and top-level `passed` is true exactly when every check passes. Empty details,
caller-selected check booleans, and a top-level result inconsistent with any
represented artifact or control decision are invalid.

After canonical `verification.json` bytes exist, an external
`ArtifactSnapshot` hashes all 22 files, including `verification.json`; sorts the
complete path/hash manifest lexically by path; and computes
`artifact_set_sha256` with the same line format. That complete digest is held by
the post-exposure envelope and append-only Log records. It is never embedded in
an included artifact.

Use the phrase `artifact-manifest document (verification.json)` throughout the
authority and tests. Do not use `artifact-manifest file`, add a second manifest,
or modify `source_digest_receipt.json`.

#### Unambiguous Hash Names

Freeze these meanings:

```text
config_sha256
  Embedded config self-hash over the canonical config payload with only
  config_sha256 omitted.

config_file_sha256
  SHA-256 over complete canonical recovery_gate_config.json bytes, including
  the embedded config_sha256 field.

receipt_sha256
  Embedded holdout-receipt self-hash over canonical receipt payload with only
  receipt_sha256 omitted.

holdout_receipt_file_sha256
  SHA-256 over complete holdout_receipt.json bytes.

preholdout_receipt_file_sha256
  SHA-256 over complete preholdout_state_receipt.json bytes. That receipt has
  no embedded self-hash.

represented_artifact_set_sha256
  verification.json's digest over the 21 represented files.

artifact_set_sha256
  External complete 22-file snapshot digest including verification.json.
```

`holdout_manifest.json.receipt_sha256` equals the embedded holdout-receipt
`receipt_sha256`, never the file-byte hash. Config bindings in verification and
both receipts use embedded `config_sha256`. Before/after envelopes use complete
file-byte hashes as well as the self-hash identities.

Typed internal identities must be equivalent to:

```python
@dataclass(frozen=True, slots=True)
class FrozenConfigIdentity:
    path: Path
    payload: Mapping[str, object]
    config_sha256: str
    config_file_sha256: str
    canonical_bytes: bytes

@dataclass(frozen=True, slots=True)
class HoldoutReceiptIdentity:
    path: Path
    payload: Mapping[str, object]
    receipt_sha256: str
    holdout_receipt_file_sha256: str
    canonical_bytes: bytes

@dataclass(frozen=True, slots=True)
class ReceiptFileIdentity:
    path: Path
    file_sha256: str
    canonical_bytes: bytes
```

Freeze these `ProvenanceEnvelope` members:

```text
config_sha256
config_file_sha256
preholdout_receipt_file_sha256
receipt_sha256
holdout_receipt_file_sha256
represented_artifact_set_sha256
artifact_set_sha256
```

Raw dicts, unchecked paths, ambiguous `sha256` strings, and swapped self/file
hashes are rejected at every phase boundary.

Required JSON top-level keys are:

- config: `schema_version`, `spec_sha256`, `config_sha256`, `source_sha256`,
  `tracked_state_sha256`, `model`, `estimator`, `parameters`, `scenarios`,
  `seed_partitions`, `gates`, `artifact_manifest`, and `boundary_labels`;
- runtime projection: `schema_version`, `workers`, `safety_factor`,
  `measured_task_units`, `equal_bootstrap_task_unit`,
  `calibration_task_durations`, `holdout_task_durations`,
  `calibration_worker_loads`, `holdout_worker_loads`,
  `projected_calibration_seconds`, `projected_holdout_seconds`,
  `holdout_payload_instantiated`, `scientific_rows_emitted`, and `passed`;
- source provenance: `schema_version`, `source_commit`, `parameter_set_id`,
  `source_apis`, `expected_counts`, `reconciled_counts`, `landscape_sha256`,
  `arrival_sha256`, and `passed`;
- holdout manifest: `schema_version`, `spec_sha256`, `config_sha256`,
  `source_sha256`, `tracked_state_sha256`, `seed_namespace`, `receipt_sha256`,
  `exposed`, `invalidated`, and `no_contract_change`;
- verification: `schema_version`, `spec_sha256`, `config_sha256`,
  `source_sha256`, `checks`, `recommendation_class`,
  `transportability_class`, `boundary_labels`, and `passed`.

For all JSON objects, `schema_version` and hashes are strings; counts and
`workers` are integers; thresholds, timings, projections, safety factors, and
parameter values are finite numbers; `passed`, `holdout_payload_instantiated`,
`scientific_rows_emitted`, `exposed`, `invalidated`, and
`no_contract_change` are booleans. No undeclared top-level key is allowed.
Required nested fields are:

- each runtime `measured_task_units` item: `task_id:str`, `scenario_id:str`,
  `benchmark_split:enum(development|calibration)`,
  `benchmark_replicate_first:int`, `benchmark_replicate_last:int`,
  `measured_duration_seconds:number`,
  `calibration_repeat_count:int`, `holdout_repeat_count:int`,
  `includes_profiles:bool`, `predictive_reference_count:int`, and
  `scientific_row:bool`; the list has one complete unit for every scenario,
  with first and last both `0` except the equal-emission timing bundle's
  development range `0, ..., 23`;
- runtime `equal_bootstrap_task_unit`: `task_id:str`,
  `benchmark_split:enum(development)`, `bundle_index:int`,
  `pseudo_replicate_first:int`, `pseudo_replicate_last:int`,
  `measured_duration_seconds:number`, `calibration_repeat_count:int`,
  `holdout_repeat_count:int`, and `scientific_row:bool`; literal values are
  bundle `0`, pseudo-replicates `0` and `23`, holdout repeat count `199`, and
  `scientific_row = false`;
- runtime `calibration_task_durations` and `holdout_task_durations`: exact
  arrays of `{task_id:str, duration_seconds:number}` objects before LPT
  assignment, with stable unique task IDs for every repeated task;
- runtime `calibration_worker_loads` and `holdout_worker_loads`: arrays of
  exactly eight finite nonnegative seconds in worker-index order after the
  frozen LPT assignment;

- `model`: `time_grid:list[number]`, `hazard_link:str`,
  `hazard_equation:str`, `observation_distribution:str`,
  `analyst_fields:list[str]`, `oracle_fields:list[str]`,
  `conditionally_independent_cells:bool`;
- `estimator`: `method:str`, `optimizer:str`, `deterministic_starts:int`,
  `convergence_tolerance:float`, `profile_level:float`, `lr_cutoff:float`,
  `root_tolerance_fraction:float`, `root_max_iterations:int`;
- each `parameters` item: every field in `model_parameter_contract.csv` except
  the two status fields, with matching types;
- each `scenarios` item: every field in `scenario_definitions.csv`, with
  matching types;
- `seed_partitions`: `master_seed:int`,
  `nested_development_replicates:int`,
  `nested_calibration_replicates:int`, `nested_holdout_replicates:int`,
  `sparse_development_replicates:int`, `sparse_holdout_replicates:int`,
  `control_development_replicates:int`, `control_holdout_replicates:int`,
  `predictive_reference_draws:int`, `equal_emission_bootstrap_bundles:int`;
- `gates`: `coverage_level:float`, `coverage_familywise_alpha:float`,
  `coverage_gate_count:int`, `negative_false_positive_rate:float`,
  `sparse_coverage_replicates:int`, `sparse_coverage_alpha:float`,
  `profile_width_limits:object`, `absolute_error_limits:object`,
  `convergence_limits:object`, `pit_familywise_alpha:float`,
  `alignment_logscore_fraction:float`,
  `alignment_correlation_limit:float`, `silent_misspecification_rule:str`;
- each `artifact_manifest` item: `path:str`, `role:enum(root|visual)`,
  `required:bool`, `sha256:str?`;
- `boundary_labels`: `synthetic_only:bool`, `scheduled_count_only:bool`,
  `fixed_arrival_surface:bool`, `no_spread_parameter_fit:bool`,
  `no_abc_mcmc_or_posterior:bool`, `no_real_data:bool`,
  `no_remote_compute:bool`, `no_production_adoption:bool`.

Required source-provenance nested fields are:

- `source_apis:list[str]` in the fixed API order above;
- `expected_counts` and `reconciled_counts`, each containing integer
  `landscape_cell_count`, `passable_cell_count`, `water_cell_count`,
  `final_colonized_passable_count`, and `finite_prey_extirpation_count`.

Each verification `checks` item contains `name:str`, `passed:bool`, and
`details:object`; check names are exactly the `gate_family` values plus
`artifact_manifest` and `tracked_state`. Nested detail keys are diagnostic and
may vary, but cannot alter gate results or recommendation precedence.

Define
`source_sha256 = sha256("landscape_sha256=" + landscape_sha256 + "\narrival_sha256=" + arrival_sha256 + "\n")`
over UTF-8 bytes.

Tracked receipt schemas are:

- `source_digest_receipt.json`: `schema_version`, `serialization_contract`,
  `source_commit`, `parameter_set_id`, `landscape_sha256`, `arrival_sha256`,
  `independent_check_landscape_sha256`,
  `independent_check_arrival_sha256`, and `passed`;
- `holdout_receipt.json`: `schema_version`, `spec_sha256`, `config_sha256`,
  `source_sha256`, `tracked_state_sha256`, `seed_namespace`,
  `receipt_sha256`, `exposed`, `invalidated`, and `no_contract_change`. Its
  `receipt_sha256` is computed with that field omitted.
- `preholdout_state_receipt.json`: `schema_version`, `spec_sha256`,
  `config_sha256`, `source_sha256`, `tracked_state_sha256`, and
  `tracked_file_manifest`; the manifest is an array of `{path, sha256}` objects
  sorted by path.

The canonical tracked-state digest is computed by SHA-256 hashing UTF-8 lines
`<file_sha256><two spaces><relative_path>\n` for every allowed tracked path
except append-only `Log.md` and the two receipt files, sorted lexically by
path. `Log.md` may record hashes but must not change equations, thresholds,
code, tests, schemas, or conclusions. The digest is verified before
holdout, after post-holdout read-only checks, before final review, and before
commit.

All CSVs use explicit headers, UTF-8, `.` decimal, empty string only for
structurally inapplicable values, and stable lexical/numeric ordering by the
keys above. JSON uses sorted keys. No NaN or infinity may be emitted.

Required self-decoding visuals:

- `visuals/parameter_recovery.svg`
- `visuals/coverage_calibration.svg`
- `visuals/latent_time_calibration.svg`
- `visuals/identifiability_profiles.svg`
- `visuals/control_comparison.svg`
- `visuals/review_montage.svg`

### Literal External Authority Completion

This subsection is the definitive transcription authority for generated bytes.
It resolves every earlier generic `enum`, `str`, schema-version, nullability,
and evidence-source reference without changing any scientific model, threshold,
seed, scenario, or recommendation rule above.

#### Scenario/parameter truth authority

Every `replicate_recovery.csv` row uses the literal value below. A
truth-bearing row retains its truth even when its fit fails or its profile is
open. Only `goal018_continuous_abundance_stress` is parameter-truth-free and
therefore uses null truth, coverage, and error fields. Equal emission emits no
recovery row.

| Scenario | Recovery parameter truths in frozen parameter order |
| --- | --- |
| `process_oracle_observed_transition` | `alpha=-6.0|beta_driver=1.25|beta_quality=-0.60` |
| `observation_oracle_fixed_transition` | `lambda_quasi=0.15|lambda_present=4.0` |
| `dense_count_exact_model` | `alpha=-6.0|beta_driver=1.25|beta_quality=-0.60|lambda_quasi=0.15|lambda_present=4.0` |
| `structured_imperfect_effort` | `alpha=-6.0|beta_driver=1.25|beta_quality=-0.60|lambda_quasi=0.15|lambda_present=4.0` |
| `sparse_expected_failure` | `alpha=-6.0|beta_driver=1.25|beta_quality=-0.60|lambda_quasi=0.15|lambda_present=4.0` |
| `zero_driver_effect_negative_control` | `alpha=-6.0|beta_driver=0.0|beta_quality=-0.60|lambda_quasi=0.15|lambda_present=4.0` |
| `permuted_arrival_alignment_stress` | `alpha=-6.0|beta_driver=1.25|beta_quality=-0.60|lambda_quasi=0.15|lambda_present=4.0` |
| `no_emission_contrast_negative_control` | no recovery rows |
| `informative_dropout_misspecification_stress` | `alpha=-6.0|beta_driver=1.25|beta_quality=-0.60|lambda_quasi=0.15|lambda_present=4.0` |
| `goal018_continuous_abundance_stress` | `alpha=null|beta_driver=null|beta_quality=null|lambda_quasi=null|lambda_present=null` |
| `spatial_frailty_stress` | `alpha=-6.0|beta_driver=1.25|beta_quality=-0.60|lambda_quasi=0.15|lambda_present=4.0` |

The recovery validator reconstructs this value from `scenario_id,parameter_id`;
it never accepts caller-declared truth. Estimate, likelihood, convergence/start,
and boundary fields reconcile to exactly one
`fit_execution_evidence.csv` row. Interval width, inclusive coverage, signed
error, and absolute error are recomputed. Profile rows reconcile to the same fit
and reproduce `2 * (fit_log_likelihood - profile_log_likelihood)`. Coverage
and predictive summaries are reconstructed from complete validated source rows;
caller-supplied counts, booleans, errors, widths, p-values, or summaries are not
authority.

#### Complete enum domains

The complete domains, in serialization order, are:

```text
scenario_role = oracle|exact_joint|expected_failure|negative_control|stress
generation_model = exact_binary|zero_driver|equal_emission|informative_dropout|continuous_abundance|spatial_frailty
fit_model = process_oracle|observation_oracle|ordered_joint|equal_emission_joint
schedule_id = process_truth|dense_6|structured_12|sparse_24
effort_rule = not_applicable|unit|structured|sparse
expected_behavior = recover|weaken_honestly|no_false_signal|unidentifiable|predictive_warning
truth_access_class = oracle_only|analyst_firewalled|stress_evaluator_only
transportability_class = scheduled_count_only_point_process_bridge_required
gate_family = process_oracle|observation_oracle|dense_joint|structured_joint|sparse_honesty|zero_driver_control|arrival_alignment_control|equal_emission_control|informative_dropout_stress|continuous_abundance_stress|spatial_frailty_stress|parameter_status|final_recommendation
recommendation_class = model_contract_failed|process_observation_confounded|observation_limited_but_calibrated|latent_response_observation_gate_passed
```

All previously declared domains remain exact. In particular,
`decision_row_type`, `fit_scope`, `fit_variant`, `split_id`,
`parameter_id`, status, metric, stratum, and gate-result domains are those
already listed above and admit no aliases.

#### Literal scenario rows

`scenario_definitions.csv` and config `scenarios` use these exact rows. The
transportability value is
`scheduled_count_only_point_process_bridge_required` in every row.

| scenario_id | role | generation | fit | schedule | effort | dev | cal | holdout | expected | truth access | scope | primary | comparator |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| `process_oracle_observed_transition` | `oracle` | `exact_binary` | `process_oracle` | `process_truth` | `not_applicable` | 12 | 24 | 48 | `recover` | `oracle_only` | `replicate` | `canonical` | null |
| `observation_oracle_fixed_transition` | `oracle` | `exact_binary` | `observation_oracle` | `structured_12` | `structured` | 12 | 24 | 48 | `recover` | `oracle_only` | `replicate` | `canonical` | null |
| `dense_count_exact_model` | `exact_joint` | `exact_binary` | `ordered_joint` | `dense_6` | `unit` | 12 | 24 | 48 | `recover` | `analyst_firewalled` | `replicate` | `canonical` | null |
| `structured_imperfect_effort` | `exact_joint` | `exact_binary` | `ordered_joint` | `structured_12` | `structured` | 12 | 24 | 48 | `recover` | `analyst_firewalled` | `replicate` | `canonical` | null |
| `sparse_expected_failure` | `expected_failure` | `exact_binary` | `ordered_joint` | `sparse_24` | `sparse` | 12 | 0 | 24 | `weaken_honestly` | `analyst_firewalled` | `replicate` | `canonical` | null |
| `zero_driver_effect_negative_control` | `negative_control` | `zero_driver` | `ordered_joint` | `dense_6` | `unit` | 12 | 0 | 24 | `no_false_signal` | `analyst_firewalled` | `replicate` | `canonical` | null |
| `permuted_arrival_alignment_stress` | `stress` | `exact_binary` | `ordered_joint` | `structured_12` | `structured` | 12 | 0 | 24 | `predictive_warning` | `stress_evaluator_only` | `replicate` | `permuted_alignment` | `correct_alignment` |
| `no_emission_contrast_negative_control` | `negative_control` | `equal_emission` | `equal_emission_joint` | `dense_6` | `unit` | 12 | 0 | 24 | `unidentifiable` | `analyst_firewalled` | `scenario_shared` | `equal_rate` | `ordered_emission` |
| `informative_dropout_misspecification_stress` | `stress` | `informative_dropout` | `ordered_joint` | `structured_12` | `structured` | 12 | 0 | 24 | `predictive_warning` | `stress_evaluator_only` | `replicate` | `canonical` | null |
| `goal018_continuous_abundance_stress` | `stress` | `continuous_abundance` | `ordered_joint` | `structured_12` | `structured` | 12 | 0 | 24 | `predictive_warning` | `stress_evaluator_only` | `replicate` | `canonical` | null |
| `spatial_frailty_stress` | `stress` | `spatial_frailty` | `ordered_joint` | `structured_12` | `structured` | 12 | 0 | 24 | `predictive_warning` | `stress_evaluator_only` | `replicate` | `canonical` | null |

#### Literal generated schema versions and values

Every generated artifact has contract version `v1`. Every embedded generated
JSON `schema_version = v1`. The accepted source receipt alone retains its
already frozen `schema_version = 1.0`. The preholdout and holdout receipt
versions are `v1`, and the holdout `seed_namespace` is exactly
`goal023-holdout-v1`.

The config model object is exactly:

```text
time_grid = 0|6|12|18|24|30|36|42|48|54|60|66|72|78|84|90|96|102|108|114|120
hazard_link = complementary_log_log
hazard_equation = 1-exp(-exp(alpha+beta_driver*G_xt+beta_quality*Q_x))
observation_distribution = Poisson(E_xt*lambda_state)
analyst_fields = cell_id|standardized_quality|predator_arrival_time|time|count|effort
oracle_fields = transition_time|latent_state
conditionally_independent_cells = true
```

The estimator object is exactly:

```text
method = exact_discrete_transition_marginal_likelihood
optimizer = L-BFGS-B
deterministic_starts = 8
convergence_tolerance = 0.000001
profile_level = 0.90
lr_cutoff = 2.705543454095404
root_tolerance_fraction = 0.00001
root_max_iterations = 100
```

The seed-partition object is exactly:

```text
master_seed = 20260711
nested_development_replicates = 12
nested_calibration_replicates = 24
nested_holdout_replicates = 48
sparse_development_replicates = 12
sparse_holdout_replicates = 24
control_development_replicates = 12
control_holdout_replicates = 24
predictive_reference_draws = 199
equal_emission_bootstrap_bundles = 199
```

The gate object retains the literal values already frozen above, including
`coverage_level=0.90`, `coverage_familywise_alpha=0.05`,
`coverage_gate_count=15`, `negative_false_positive_rate=0.10`,
`sparse_coverage_replicates=24`, `sparse_coverage_alpha=0.05`,
`pit_familywise_alpha=0.01`, `alignment_logscore_fraction=0.90`, and
`alignment_correlation_limit=0.25`. Its profile-width, absolute-error,
convergence, and silent-misspecification values are exactly those already
listed. Every one of the eight boundary-label keys is exactly `true`.

#### Complete 22-artifact registry

| Artifact | Version/format | Complete identity and authoritative source |
| --- | --- | --- |
| `recovery_gate_config.json` | `v1` canonical JSON | Exact config top-level/nested keys above; embedded self-hash with only `config_sha256` omitted. |
| `runtime_projection.json` | `v1` canonical JSON | Exact top-level and nested runtime keys above; task IDs are unique and sorted in declared task order; eight worker loads; no additional keys. |
| `source_provenance.json` | `v1` canonical JSON | Exact source keys/count objects above; source APIs in frozen order; accepted source hashes and `passed=true`. |
| `holdout_manifest.json` | `v1` canonical JSON | Same ten fields and literal exposure values as the immutable holdout receipt; `receipt_sha256` is the embedded receipt hash. |
| `model_parameter_contract.csv` | `v1` UTF-8 CSV | Exact 11-column header/schema and five-row frozen parameter order above; no nullable field. |
| `scenario_definitions.csv` | `v1` UTF-8 CSV | Exact 15-column header/schema and 11 rows above; only comparator is nullable under the literal rows. |
| `fit_execution_evidence.csv` | `v3` UTF-8 CSV | Exact 36-column normalized fit/design header/schema, seven-part key, typed fit-failure class, explicit row-kind sort, fit/design nullability, diagnostic applicability, cell-frame digests, supports, and source identities above. |
| `replicate_recovery.csv` | `v1` UTF-8 CSV | Exact 19-column header/schema/key; truth authority and failed/open/continuous row states in this subsection. |
| `coverage_calibration.csv` | `v1` UTF-8 CSV | Exact 16-column header/schema/key; every count and summary is reconstructed from a complete recovery/fit frame. |
| `latent_time_calibration.csv` | `v1` UTF-8 CSV | Exact 12-column header/schema/key; exactly three rows per attempted identity and the applicable/unavailable/N/A states above. |
| `predictive_replicate_diagnostics.csv` | `v1` UTF-8 CSV | Exact 20-column header/schema/key; exactly 27 rows per attempted identity, bound opportunity-frame/mask evidence, and complete metric algebra above. |
| `predictive_check_summary.csv` | `v1` UTF-8 CSV | Exact 16-column header/schema/key; 27 cells per scenario/split/variant and complete-source reconstruction. |
| `identifiability_profiles.csv` | `v1` UTF-8 CSV | Exact 11-column header/schema/key; contiguous grid, finite successful points, and fit-likelihood delta reconstruction. |
| `control_decision_summary.csv` | `v1` UTF-8 CSV | Exact 24-column header/schema and lexical ID sort; 11 scenario rows, six fixed parameter-status rows, one final row. |
| `verification.json` | `v1` canonical JSON | Exact verification keys above; check names are the 13 `gate_family` values plus `artifact_manifest` and `tracked_state`. |
| `report.md` | `v1` UTF-8 Markdown | Links config, runtime, source, holdout, all nine CSVs, control summary, and verification directly; states recommendation and transportability. |
| `visuals/parameter_recovery.svg` | `v1` UTF-8 SVG | Reads only `model_parameter_contract.csv` and `replicate_recovery.csv`. |
| `visuals/coverage_calibration.svg` | `v1` UTF-8 SVG | Reads only `coverage_calibration.csv`. |
| `visuals/latent_time_calibration.svg` | `v1` UTF-8 SVG | Reads only `latent_time_calibration.csv`. |
| `visuals/identifiability_profiles.svg` | `v1` UTF-8 SVG | Reads only `identifiability_profiles.csv`. |
| `visuals/control_comparison.svg` | `v1` UTF-8 SVG | Reads only `fit_execution_evidence.csv` and `control_decision_summary.csv`. |
| `visuals/review_montage.svg` | `v1` UTF-8 SVG | Reads the preceding five SVGs in their literal order and no scientific table directly. |

For `coverage_calibration.csv`, nested holdout acceptance bounds are
`36..48`; sparse holdout bounds are `18..24`; descriptive-stress bounds are
null. `coverage_fraction=coverage_count/replicate_count`. Failed/open profiles
contribute the complete natural-support width and are uncovered. Failed fits
contribute the complete support width to absolute-error summaries. Finite
signed-error medians use only successful truth-bearing rows. All contributing
values must be finite and nonnegative.

For `predictive_check_summary.csv`, each summary cell consumes exactly one
matching row from every attempted replicate. `diagnostic_count` counts
available rows and `failed_fit_count` counts failed fits. The mean residual is
the arithmetic mean of finite standardized residuals. `stouffer_z` is their
sum divided by the square root of their count. The two-sided one-sample
Kolmogorov-Smirnov statistic is computed from sorted PIT values; its exact
finite-sample survival probability is `raw_p`. Holm values are recomputed
jointly across the 27 cells in frozen order. Any incomplete source, failed fit,
unavailable diagnostic, nonfinite residual state, or null required aggregate
sets `warning=true` and `gate_result=fail`.

The six equal-emission parameter-status rows are exactly:

```text
alpha,unidentified,unidentified
beta_driver,unidentified,unidentified
beta_quality,unidentified,unidentified
lambda_quasi,unidentified,unidentified
lambda_present,identified,not_applicable
lambda_equal,identified,identified
```

They use `decision_row_type=parameter_status`,
`gate_family=parameter_status`, and `gate_result=diagnostic`; all
statistic/count/recommendation fields are null. Scenario rows use the
scenario-corresponding gate family. The final row uses
`gate_family=final_recommendation`. All rows have
`silent_misspecification_failure:bool!`, the literal transportability class,
and nonempty interpretation. No caller boolean may stand in for these rows.

All 18 rows are reconstructed before comparison with emitted bytes. A scenario
row's `interpretation` is its canonical reducer reason, `gate_result=pass`
exactly for reason `pass` and otherwise `fail`, and
`silent_misspecification_failure=true` exactly for a canonical
`*_silent_misspecification` reason. Arrival correlation is recomputed from the
accepted fixed source values and deterministic within-block permutation, never
read from the row. The six status-row interpretations are exactly
`equal_emission_parameter_status`. The final row is recomputed from all eleven
scenario reasons: its rank/class/reason come from the global reducer, its gate
passes only at rank four, and its interpretation equals that reason. Emitted
rows must equal this reconstruction field for field.

#### Report links and visual sources

`report.md` links these root evidence files in literal bundle order:
`recovery_gate_config.json`, `runtime_projection.json`,
`source_provenance.json`, `holdout_manifest.json`,
`model_parameter_contract.csv`, `scenario_definitions.csv`,
`fit_execution_evidence.csv`, `replicate_recovery.csv`,
`coverage_calibration.csv`, `latent_time_calibration.csv`,
`predictive_replicate_diagnostics.csv`, `predictive_check_summary.csv`,
`identifiability_profiles.csv`, `control_decision_summary.csv`, and
`verification.json`. The six visual source bindings are exactly those in the
22-artifact registry and cannot be replaced by live fit objects.

#### Closed post-holdout command and repository state

Runbook section 7's twelve argv vectors are the complete closed
non-generative-command registry. Each registry row binds exact argv, command
class, parsed phase, and reviewed transient disposition. Retry and Task 6 reject
an unregistered vector before execution; substring classification has no
authority.

Publication captures the resolved checkout root and resolved Git common
directory for every state. Commit states use the Goal worktree; merge and push
states use the distinct canonical checkout. All share one common object store
and the approved commit tree equals the validated pre-commit `git write-tree`.
Parent and local/remote ref transitions remain exactly those in Runbook section
9.

A terminal record is one canonical JSON line with
`record_type=terminal_attestation`, bound to the resolved repository root and
the exact relative path
`docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`.
The complete pre-append envelope is embedded. Any prior terminal record forbids
another, even with a new parent. The guarded append models the Log worktree
bytes, index/cached Log blob, and porcelain status transition while preserving
every non-Log blob. A post-append mismatch yields
`STOP_INVALIDATED_TERMINAL_ATTESTATION_IMMUTABLE`; it never yields acceptance
or permits another append.


### Final Rereview 6 Integrated Decision Authority

This section is a literal completion of the existing model and threshold
authority, not a scientific change. The complete science bundle consumes the
single normalized `fit_execution_evidence.csv` v3 table, partitions exact
fit-result and design-diagnostic frames, and reconstructs every design input
from persisted rows. It never infers design state from `fit_succeeded` and
never inserts a rank, condition, pass, provenance, or role constant during
reduction. Missing, duplicate, foreign, reordered, nonfinite, or inapplicable
design rows fail closed before a gate.

`JointFitResult` is fail-closed. `converged=true` requires accepted natural
parameters, a converged joint multistart, passing typed potential and plug-in
diagnostics, and null failure. A failed potential or plug-in design cannot
coexist with convergence or accepted parameters. When optimization converges
but the plug-in gate fails, the result is `converged=false`, parameters are
null, the converged multistart and failed diagnostic remain available for
audit, and failure is `joint_plugin_design_gate_failed`.

### Final Rereview 7 Fail-Closed Completion

The in-memory `DesignDiagnostic` algebra is authoritative and is invoked by
every joint/process result constructor. Provenance and role are nonempty exact
builtin strings; dimensions are positive exact builtin integers; rank is an
exact builtin integer in `0..min(n_rows,n_columns)`; and `passed` is an exact
builtin Boolean derived, never trusted. Full rank additionally requires
`n_rows >= n_columns` and a finite condition at least 1. Rank deficiency uses
positive infinity in memory and null in persisted CSV; NaN is always invalid.
Pass is exactly full rank with condition strictly below `1e8`. Failure is null
if and only if pass. Forged rank/pass,
condition/pass, nonfinite, dimension, or failure states are rejected even when
attached to otherwise converged joint or process-oracle results.

Persisted fit/design rows are validated individually, partitioned by the exact
five-part fit identity, checked against the complete applicable design frame,
then passed through the state machine above. No contradictory fit/design bundle
can reach a local reason, control row, recommendation class, or verification
document. Failed diagnostics remain available for audit, but accepted
parameters and convergence do not.

The deterministic pre-Task-3 acceptance fixture reconstructs each predictive
sample size from the same retained typed opportunities used by metric
calculation. Canonical serialization includes cell, time, exact effort, quality
stratum, time band, keyed keep identity, and keep/drop state. Its
informative-dropout fixture mask is deterministic fixture evidence only: it is
hashed and fixed without constructing a production RNG or payload. The
production adapter authenticates the actual canonical schedule and realized
fixed keyed mask under the same count/digest contract. This completion changes
no production schedule, dropout mechanism, seed namespace, or stochastic
authority.

### Final Rereview 8 Typed Frame And Failure Completion

The joint fitter requires a module-issued `AnalystFitFrame` before potential
design construction or objective evaluation. The history IDs must equal its
exact canonical ID tuple. `JointFitResult` carries the frame, count, and digest,
and persisted joint design fields are derived only from that validated result.
Arrival therefore admits exactly 4180 fit histories and 83600 potential and
plug-in rows; score histories, fit/score swaps, and 5225-cell substitutions stop
before optimization.

Every in-memory and persisted design obeys
`rank <= min(n_rows,n_columns)`, and pass requires at least as many rows as
columns. Typed fit failure classes and the explicit transition table above are
the sole failure provenance. Optimizer/nonfinite failures require rank-zero
joint/process downstream diagnostics; evaluated rank/condition diagnostics
require the matching gate class; potential failure carries no optimizer-result
field. Every transition is exercised against the complete deterministic bundle
before reduction, including process, observation, and equal-rate applicability
exceptions.

Predictive frames are module-issued from an exact production or fixture
schedule adapter. The canonical semantic serialization and keyed dropout mask
bind every retained sample size and all 27 metric cells. Equal-cardinality
quality/time swaps, effort mutation, metric-specific size mutation, fit/score
frame mutation, and keyed-mask mutation are invalid before summary or
recommendation. These repairs retain the exact 22 artifact paths and all frozen
scientific and stochastic authority.

For each predictive-applicable scenario's exact holdout replicate and summary
frame, reconstruct these values in this order:

```text
predictive_complete_finite =
    every required fit and all 27 cells per attempted replicate are available
    and every required residual and summary aggregate is finite
finite_rule_fired =
    any finite Holm-adjusted p < 0.01 or any finite abs(Stouffer Z) > 3
forced_warning = not predictive_complete_finite
scientific_warning_available = predictive_complete_finite and finite_rule_fired
predictive_pass = predictive_complete_finite and not finite_rule_fired
```

The boundaries are open: adjusted p exactly `0.01` and absolute Stouffer Z
exactly `3` do not warn. If forced evidence and a finite rule coexist in
different cells, `forced_warning=true` takes precedence and
`scientific_warning_available=false`; the finite rule remains visible as
`finite_rule_fired=true`. Failed or missing fits/cells, null required
aggregates, and nonfinite residual flags are forced/incomplete evidence and
cannot satisfy arrival, dropout, continuous-abundance, or frailty warning
requirements.

Zero-driver evidence adds required Boolean `predictive_pass`. It is populated
only from the exact holdout predictive frame above. The exclusion decision can
pass only when all 24 intervals are decidable, exclusions are `0..6`, plug-in
evidence is available, and `predictive_pass=true`; a finite Holm or Stouffer
rejection is `contract_failure:zero_driver_unavailable`.

The integrated deterministic acceptance fixture traverses the exact complete
identity frame: `990` fit identities, `1695` design rows, `2340` recovery rows,
`11700` profile points, `105` coverage rows, `552` latent identity groups,
`504` predictive identity groups, `23` predictive-summary groups, and exactly
`18` control rows. It reaches all eleven local `pass` reasons and final rank
`4`, class `latent_response_observation_gate_passed`. Its arrival and
continuous-abundance warnings are finite scientific rules; dropout and frailty
are finite complete non-warning states with no narrow-wrong result.

Each verification scenario-check detail has exactly the existing decision ID,
gate and reason plus `design_evidence_sha256`, `design_row_count`,
`predictive_complete_finite`, `predictive_pass`, `finite_rule_fired`,
`scientific_warning_available`, and `forced_warning`. The design digest is
canonical JSON over all 1695 validated persisted design rows in artifact sort
order. Recommendation class and top-level pass continue to derive from the
reconstructed 18-row control decision, so any decisive design, prediction, or
warning mutation propagates through local reason, final rank/class, and
verification.

`report.md` retains the same literal root links because design evidence is
normalized inside the already declared fit-execution artifact.
`control_comparison.svg` consumes both row kinds from that artifact and the
reconstructed control table. The artifact count remains exactly 22; no new
path, stochastic phase, threshold, model equation, seed, or publication
authority is introduced.

## Required Source Footprint

Create:

- `spec/synth_medium_latent_response_observation_recovery_gate.md`
- `src/spatext/observe.py`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- `scripts/run_synth_medium_latent_response_observation_recovery.py`
- `tests/test_observe.py`
- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json`

Modify as needed:

- `pyproject.toml`
- `uv.lock`
- `AGENTS.md`
- `README.md`
- `spec/report_log.md`
- `src/spatext/synth/medium/__init__.py`

## Acceptance And Stop Rules

Acceptance requires analytic toy validation, observed red-green TDD evidence,
all four nested gates, correctly failing controls, source/artifact
reconciliation, scheduled-count transportability language, full validation,
and independent scientific, provenance, code, artifact, and final staged-diff
review with no open critical or important findings.

Provenance acceptance additionally requires the complete per-command envelope,
exact pinned branch/HEAD/base and candidate-footprint guards at config emission,
freeze, pre-receipt, and pre-RNG, and a terminal disposition for every nonzero
validation under the one-retry rule. These are provenance gates only and
cannot alter a scientific gate or result.

Stop on oracle failure, negative-control false signal, unresolved accepted
estimand ridge, confidently wrong sparse inference, unreported missingness bias,
numerical-domain failure, canonical noncollision/design-audit failure,
holdout-lock breach, unavailable case-study exposure/zero fields being treated
as observed, need for full spread fitting, real data, remote compute, or a new
material biological assumption.

## Non-Goals

- Changing Goal 017 or Goal 018 outputs.
- Fitting Goal 019-022 data or reconstructed targets.
- Inferring predator spread, conductance, or Goal 018 impact parameters.
- ABC, MCMC, posterior claims, real data, remote compute, or production-model
  adoption.

## Authority

Barry's standing instruction authorises exact-footprint commit and publication
after orchestrator acceptance, full validation, and independent final review.
Generated artifacts and build outputs remain ignored and unstaged. Any material
scientific assumption or genuine strategic trade-off returns to Barry first.
