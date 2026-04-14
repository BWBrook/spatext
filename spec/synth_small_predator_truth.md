# `synth-small` Deterministic Predator-Response Truth Module

## Purpose

This document specifies the next substantive modelling module for `spatext`
after completion of the prey-only `synth-small` baseline and its first
inspection pass.

The next step is to introduce the spreading predator onto the existing
landscape and generate the first full latent driver-response truth object for
the synthetic system.

This module should create, in deterministic form:

- a predator arrival-time surface `T_P(x)`,
- a time-varying predator-pressure field `P_t(x)`,
- a prey abundance trajectory `N_t(x)` after predator introduction,
- a latent true extirpation-time surface `T_X^{true}(x)`,
- a lag surface relating extirpation timing to predator arrival.

This is the first module that completes the core scientific chain from
spreading driver to extirpation response.

## Executive decisions

### 1. Predator next, not stochasticity

The next main increment should be the deterministic predator-response module,
not a stochastic elaboration of the prey-only baseline.

Why:

- the central scientific question is about linking a spreading driver to an
  extirpation response,
- the current repo already has a clean deterministic prey baseline,
- adding stochasticity now would make the system harder to diagnose before the
  main driver-response machinery is in place,
- stochasticity is better treated next as a robustness layer on top of an
  already validated deterministic truth module.

So for this step:

- keep the prey dynamics deterministic,
- keep the predator process deterministic,
- postpone environmental and demographic stochasticity to a later module.

### 2. Reuse the current baseline as the initial condition

The new predator-response module should build directly on the existing
`synth-small` baseline.

That means:

- same spatial domain,
- same suitability surface,
- same carrying-capacity surface,
- same equilibrium prey abundance as the pre-predator initial state.

The predator module should not fork or duplicate baseline logic.

### 3. Treat the predator as exogenous in v1

For this synthetic example, the predator should be treated as a spreading
generalist driver rather than as a population whose abundance is numerically
coupled to the focal prey.

In practice:

- do **not** introduce a separate predator state variable in this step,
- do **not** make predator spread depend on current focal-prey abundance,
- do **not** make predator pressure collapse as the focal prey declines.

Instead, represent the predator by:

- an arrival-time surface `T_P(x)`,
- a bounded post-arrival pressure ramp,
- a prey mortality term that acts on the prey but does not feed back onto the
  driver process.

This matches the intended “generalist predator” scientific story and keeps the
inferential target clean.

### 4. Default to a Type II prey response

The default prey mortality response to predator pressure should be Type II.

That is the preferred default because it provides:

- exogenous predator pressure that does not grant the focal prey an automatic
  low-density refuge,
- a better match to the intended generalist-predator story for this first
  deterministic module,
- a cleaner scientific story for a generalist predator.

The implementation should be structured so alternative response forms can be
added later, but the required v1 default is Type II.

### 5. Keep the first predator module scientifically informative, not maximal

The first default parameterisation should produce a mixed response regime:

- predator arrival should sweep across the domain,
- prey abundance should decline after arrival,
- some cells should extirpate by the end of the run,
- some cells should remain above the extirpation threshold.

Avoid trivial default regimes where:

- almost nothing happens,
- everything extirpates almost immediately,
- the lag surface is nearly constant or uninformative.

The point is to create a useful synthetic truth benchmark for later
observation and recovery work.

## Scope

This module covers deterministic predator introduction and deterministic prey
response on the existing `synth-small` landscape.

It includes:

- deterministic predator arrival,
- deterministic predator-pressure ramping,
- deterministic prey decline under predator pressure,
- latent true extirpation timing,
- artifact emission for the resulting truth object.

It does **not** include:

- stochastic prey dynamics,
- stochastic predator spread,
- observation models,
- reconstructed `T_X^{obs}(x)`,
- parameter recovery,
- posterior inference,
- a predator numerical-response model.

## Scientific object to be produced

The goal of this module is to generate one clean latent truth object of the
form

$$
\left(
\mathcal{X},
S,
K,
N_0,
T_P,
P_t,
N_t,
T_X^{\mathrm{true}}
\right),
$$

where:

- `\mathcal{X}` is the domain graph,
- `S(x)` is suitability,
- `K(x)` is carrying capacity,
- `N_0(x)` is the pre-predator equilibrium abundance from the baseline module,
- `T_P(x)` is predator arrival time,
- `P_t(x)` is time-varying predator pressure,
- `N_t(x)` is the post-introduction prey trajectory,
- `T_X^{true}(x)` is latent extirpation time.

## Driver-arrival specification

### General rule

The predator should be introduced through an explicit arrival-time surface
rather than by an implicit pressure field.

The recommended construction is graph-based so it remains consistent with the
repo’s tessellation-agnostic design.

### Default source geometry

The default `synth-small` predator introduction should use a western-boundary
source set.

Let

$$
B_W = \{x \in \mathcal{X} : \mathrm{col}(x) = 0\}.
$$

Then define graph distance from that source set by

$$
d_G(B_W, x) = \min_{z \in B_W} d_G(z, x).
$$

The default arrival surface should then be

$$
T_P(x) = t_{\mathrm{intro}} + \left\lceil \frac{d_G(B_W, x)}{v_P} \right\rceil,
$$

where:

- `t_intro` is the introduction time,
- `v_P` is the predator-front speed in graph cells per time step.

This creates a clear directional invasion front while remaining graph-native.

### Why this default is preferred

The western-boundary source set is preferable to a single interior seed for
the first deterministic module because it yields:

- a visually interpretable front,
- a clearer lag structure,
- an easier benchmark for later front-oriented summaries,
- less immediate sensitivity to radial symmetry artefacts.

Alternative source geometries can come later.

## Predator-pressure specification

Arrival is not itself the impact. The prey should respond to a time-varying
pressure field derived from arrival.

Let

$$
\Delta_t(x) = t - T_P(x).
$$

Use the bounded post-arrival ramp

$$
\widetilde{P}_t(x) =
\begin{cases}
\rho_0, & \Delta_t(x) < 0, \\
\max\!\left\{\rho_0,\;
\min\!\left(1,\; 0.2 + 0.8\,\sigma\!\left(k_{\mathrm{ramp}}
\left[\Delta_t(x) - \frac{r_{\mathrm{ramp}}}{2}\right]\right)\right)\right\},
& \Delta_t(x) \ge 0,
\end{cases}
$$

with

$$
\sigma(z) = \frac{1}{1 + e^{-z}},
\qquad
k_{\mathrm{ramp}} = \frac{6}{r_{\mathrm{ramp}}}.
$$

For v1, the final pressure field should be

$$
P_t(x) = s_{\mathrm{pred}}\,\widetilde{P}_t(x)^\gamma.
$$

The default first module should use:

- a spatially uniform pressure multiplier after arrival,
- zero or near-zero pre-arrival leakage,
- no dependence of predator pressure on focal-prey abundance.

Optional spatial modulation can come later if scientifically needed.

## Prey-response dynamics

### Initial condition

The prey initial condition for the predator-response phase must be the
equilibrium abundance from the existing baseline module:

$$
N_0(x) = N^\ast(x).
$$

### Local update

The prey should then evolve under the existing deterministic kernel with
predator mortality added:

$$
\widetilde{N}_{t+1}(x)
=
N_t(x)\,
\exp\!\Big(
r(x)\,A_{\mathrm{allee}}(N_t(x))
\left[1 - \frac{N_t(x)}{K(x)}\right]
- M_t(x)
- d
\Big),
$$

followed by graph-based dispersal

$$
N_{t+1}(x)
=
(1-\alpha)\,\widetilde{N}_{t+1}(x)
+
\alpha\,(\mathcal{K}\widetilde{N}_{t+1})(x).
$$

The implementation should preserve the basic baseline-demography structure so
the effect of predator introduction is easy to isolate.

### Predation mortality

The required default is Type II, expressed here as a per-capita mortality term:

$$
M_t(x) =
c \, P_t(x)\,\frac{h}{h + N_t(x)}.
$$

Interpretation:

- `c` is the overall predation-response scale,
- `h` is the half-saturation parameter,
- low prey abundance does not create a built-in refuge from predator pressure,
- per-capita vulnerability is highest when focal prey are scarce,
- predator pressure still remains exogenous at the system level.

### Allee effects

Do not make nonzero Allee effects a required part of the first predator module.

The implementation may continue using the current no-Allee default if that
keeps the first truth module cleaner and easier to debug. Stronger low-density
complexity can be added later if needed.

## Latent extirpation-time surface

This module must produce the first latent true extirpation-time surface

$$
T_X^{\mathrm{true}}(x).
$$

For deterministic v1, the threshold should be an absolute quasi-extinction
floor rather than a cell-wise fraction of local baseline abundance:

$$
\tau_{\mathrm{true}}(x) = \tau_{\mathrm{QE}}.
$$

Here `\tau_{\mathrm{QE}}` is a positive abundance threshold applied uniformly
across the grid.

Why this default is preferred for the current module:

- it keeps extirpation semantics interpretable as a common quasi-extinction
  standard,
- it avoids hard-coding lower extirpation thresholds in naturally sparse cells,
- it separates the deterministic v1 truth object from later low-density process
  refinements such as explicit Allee effects.

Then:

$$
T_X^{\mathrm{true}}(x)
=
\inf\left\{
t > 0 :
N_{t-1}(x) > \tau_{\mathrm{true}}(x)
\;\wedge\;
N_t(x) \le \tau_{\mathrm{true}}(x)
\right\}.
$$

If a cell does not extirpate by the end of the simulation horizon, its
`T_X^{true}(x)` should be recorded as missing rather than forced to an
arbitrary terminal value.

The module should also derive the true lag surface

$$
L(x) = T_X^{\mathrm{true}}(x) - T_P(x)
$$

for cells with finite extirpation time.

## Simulation horizon

The run horizon should be long enough to allow both:

- predator arrival across the full domain,
- post-arrival prey decline and extirpation lag.

The recommended default is:

$$
T_{\mathrm{end}} = \max_x T_P(x) + b_{\mathrm{lag}},
$$

where `b_lag` is a post-arrival buffer.

The default should be chosen so the synthetic benchmark yields a mixed and
scientifically informative state by the end of the run.

## Default scientific target regime

The default parameterisation should be tuned to produce a benchmark that is
useful for later inference experiments.

Recommended qualitative targets:

- a clear west-to-east predator front,
- visible delay between arrival and extirpation,
- substantial but incomplete extirpation by `T_end`,
- strong enough signal that a later observation layer has something real to
  recover,
- enough survivors that the system is not a trivial collapse.

As a practical guide, the default should aim for an intermediate extirpation
fraction rather than values near `0` or `1`.

## Artifact contract

This module should emit a self-contained artifact bundle for the predator truth
run.

Suggested default output directory:

`artifacts/synth_small_predator_truth`

Required files:

- `domain.json`
- `baseline_config.json`
- `predator_config.json`
- `diagnostics.json`
- `summary.json`
- `cells.csv`
- `surfaces.npz`
- `trajectories.npz`
- `suitability.svg`
- `initial_abundance.svg`
- `driver_arrival.svg`
- `true_extirpation.svg`
- `extirpation_lag.svg`
- `final_abundance.svg`

### `surfaces.npz`

At minimum, this should contain:

- `suitability`
- `carrying_capacity`
- `initial_abundance`
- `driver_arrival`
- `extirpation_threshold`
- `true_extirpation`
- `extirpation_lag`
- `final_abundance`

### `trajectories.npz`

For `synth-small`, the full deterministic trajectories should be stored because
the domain is tiny and the extra audit value is high.

At minimum, store:

- prey abundance trajectory `N_t`
- predator pressure trajectory `P_t`

### `cells.csv`

At minimum, include:

- `cell_id`
- `row`
- `col`
- `suitability`
- `carrying_capacity`
- `initial_abundance`
- `driver_arrival`
- `extirpation_threshold`
- `true_extirpation`
- `extirpation_lag`
- `final_abundance`
- `extirpated_by_end`

### `summary.json`

This should include at least:

- min, max, mean, and standard deviation of key surfaces,
- number and fraction of extirpated cells,
- number and fraction of surviving cells,
- range of `T_P(x)`,
- range of finite `T_X^{true}(x)`,
- range of finite lag values.

### `diagnostics.json`

This should record enough information to audit the run, including:

- simulation horizon,
- predator source geometry,
- front-speed parameter,
- predation-response form,
- extirpation-threshold form and threshold value,
- whether the run stayed finite and non-negative,
- whether any numerical clipping or edge-case handling was used.

## Implementation guidance

Suggested package placement:

- `spatext.synth.small.predator`

Suggested script entrypoint:

- `scripts/build_synth_small_predator_truth.py`

The implementation should reuse the current baseline module programmatically
rather than recreating suitability or equilibrium logic independently.

## Testing requirements

The new module should come with tests covering at least:

- successful deterministic run and artifact emission,
- reproducibility under fixed configuration,
- valid and finite `T_P(x)` surface,
- bounded predator pressure,
- finite non-negative prey trajectories,
- valid missing-or-finite `T_X^{true}(x)` semantics,
- consistency between `cells.csv`, `surfaces.npz`, and summary outputs,
- mixed default regime with some extirpated and some surviving cells,
- default vulnerability pattern that does not make low-density cells
  systematically safer than high-density cells,
- failure on clearly invalid configuration values.

## Acceptance criteria

This work package is complete when all of the following are true:

- `spat` can build one deterministic predator-response truth bundle from the
  existing baseline machinery,
- the predator is represented exogenously by `T_P(x)` and `P_t(x)`,
- the prey response uses deterministic decline on the baseline landscape,
- the bundle contains `T_X^{true}(x)` and the lag surface,
- the full run is reproducible,
- the default benchmark is non-degenerate,
- all required tests pass under the repo’s standard quality lane.

## What comes after this

Once this deterministic truth module exists, the next sensible stages are:

1. inspection tooling for the predator-response bundle,
2. a first canonical review run of the new bundle,
3. an observation model layered onto this truth object,
4. stochastic robustness variants of the prey and/or observation process.

Stochasticity should therefore be treated as a later stress-test module, not
as the immediate next blocker.
