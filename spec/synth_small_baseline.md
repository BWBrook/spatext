# `synth-small` Baseline Module

## Purpose

This document specifies the first substantive modelling module for `spatext`.
Its role is to create a deliberately small, fully known synthetic system that
we can use as the anchor for later simulation, observation, and parameter
recovery work.

This module is not yet about predator arrival or extinction inference. Its job
is to create the baseline prey landscape before predator introduction:

- a known spatial domain,
- a known habitat/suitability surface,
- a known prey-only population model,
- a known equilibrium distribution of the prey.

That equilibrium state will become the starting condition for later modules.

## Executive decisions

### 1. Suitability comes first

Yes. The first module should begin with a habitat or suitability surface before
we populate the landscape with prey.

This is the right order because:

- it gives the prey distribution a spatial cause before any predator is added,
- it produces a known baseline heterogeneity in density and occupancy,
- it lets us separate habitat-driven structure from predator-driven structure in
  later modules,
- it matches the more general theory already recorded in
  [`spec/theory.md`](theory.md).

### 2. Keep the first version simple

For `synth-small` v1, use:

- one static suitability layer,
- one prey species,
- deterministic prey-only dynamics,
- no predator,
- no observation model,
- no parameter fitting,
- no time-varying habitat erosion.

The point is to create a stable, auditable baseline truth object, not to add
all later realism immediately.

### 3. Baseline goal

The goal of this module is:

> Starting from a known suitability surface and a known prey-only dynamical
> model, generate a prey abundance surface that is at equilibrium before the
> novel predator is introduced.

### 4. Tessellation recommendation

Hexes are attractive in principle, but I do **not** recommend making them the
first concrete implementation target for `synth-small`.

The recommendation is:

- use a `25 x 25` square lattice for `synth-small` v1,
- but implement the spatial domain internally as a generic cell graph so that a
  hex version can follow without redesigning the whole module stack.

Why:

- the first module should optimise for tractability, testability, and rapid
  iteration,
- the theoretical commitments we already distilled from `exdyn-sandbox` are
  easier to port cleanly onto a square lattice first,
- a square benchmark is sufficient for establishing the tooling, baseline
  equilibrium logic, and synthetic audit trail,
- the hex-vs-square question is more important for front geometry and isotropy
  in later spread modules than for the initial prey-only equilibrium module.

So the right compromise is:

- **square first**
- **graph abstraction from day one**
- **hex as the first planned variant, not the first blocker**

## Domain specification

### Spatial domain

The `synth-small` domain is:

- a `25 x 25` lattice,
- interpreted as a complete island,
- with no habitat cells beyond the border.

This is intentionally small enough to:

- run instantly,
- visualise easily,
- inspect cell-by-cell if needed,
- support exhaustive testing and sanity checks.

### Boundary interpretation

The user’s island framing is good because it makes the outer boundary
scientifically explicit rather than a hidden truncation artefact.

For the first module, however, the boundary treatment should be:

- no external source population,
- no hidden wrap-around,
- dispersal defined only over in-island cells,
- neighbor structure made explicit through a domain graph.

For `synth-small` v1, dispersal weights should be renormalized over valid
in-domain neighbors rather than sending biomass into implicit outside cells.

Rationale:

- this keeps the first equilibrium module focused on habitat-driven baseline
  structure rather than coastline sink effects,
- it avoids making boundary-loss dynamics a hidden extra mechanism in the first
  benchmark,
- it still respects the island framing because nothing exists outside the
  domain.

If we later want explicit hostile-matrix emigration loss, that should be added
as a separate model extension, not smuggled into the first baseline module.

## Suitability layer specification

### General rule

The baseline prey distribution should be induced by a static suitability
surface

$$
S(x) \in [0,1],
$$

defined over all island cells.

This surface is part of the known synthetic truth.

### Initial complexity level

Use exactly **one** composite suitability layer in v1.

Do **not** begin with:

- multiple named habitat layers,
- time-varying suitability,
- stochastic annual habitat fluctuations,
- binary habitat masks with holes,
- suitability inferred from pseudo-real covariates.

Those are later extensions.

### Recommended generative form

The suitability surface should be smooth and spatially structured, but simple
enough to be fully interpretable.

Recommended pattern:

$$
S(x) = \mathrm{clamp}\!\left(
w_0 + w_1 G_1(x) + w_2 G_2(x) + w_3 L(x),
\; 0,\; 1
\right),
$$

where:

- $G_1(x)$ and $G_2(x)$ are broad Gaussian bumps,
- $L(x)$ is an optional low-amplitude linear gradient,
- the weights are fixed and recorded,
- all parameters are deterministic under a fixed seed or, preferably, fully
  specified directly.

This gives us:

- smooth internal heterogeneity,
- no sharp artificial habitat edges,
- a surface that is easy to visualise and reason about.

### Why not multiple suitability layers yet

A multi-layer habitat model can wait. For the first module, we only need enough
spatial structure to generate a non-uniform equilibrium prey distribution.

One composite surface is enough to test:

- grid/domain construction,
- parameter plumbing,
- equilibrium finding,
- output objects and plotting,
- later observation and recovery tooling.

## Prey-only baseline dynamics

### Core idea

The prey should be simulated under the general dynamical form already recorded
in [`spec/theory.md`](theory.md), but with the predator absent:

$$
P_t(x) = 0.
$$

The first baseline module should therefore inherit the future model family
without yet activating the predator-response part.

### Recommended v1 formulation

Use a deterministic prey-only update of the form

$$
\widetilde{N}_{t+1}(x)
=
N_t(x)\,
\exp\!\Big(
r(x)\,A_{\mathrm{allee}}(N_t(x))
\left[1 - \frac{N_t(x)}{K(x)}\right]
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

For v1:

- $P_t(x)=0$ everywhere,
- $K(x)$ should depend on suitability,
- $r(x)$ may either be constant or suitability-modulated,
- $d$ should be spatially constant unless there is a strong reason otherwise.

### Mapping suitability to demographic quantities

The simplest recommended mapping is:

$$
K(x) = K_{\max}\,f_K(S(x)),
$$

with

$$
f_K(S) = k_{\min} + (1-k_{\min})S,
\qquad 0 < k_{\min} < 1.
$$

This guarantees:

- strictly positive carrying capacity in every island cell,
- higher equilibrium densities in better habitat,
- a very transparent relationship between suitability and prey baseline.

Optionally, growth can also be suitability-modulated:

$$
r(x) = r_{\max}\,f_r(S(x)).
$$

For the first module, I recommend:

- suitability affects **carrying capacity first**,
- growth modulation is optional and may be deferred.

That keeps the equilibrium story simpler.

### Allee effect

The baseline module may include an Allee term if we want continuity with the
full model class:

$$
A_{\mathrm{allee}}(N) = 1 - \frac{A}{N + A}.
$$

But for `synth-small` v1 the Allee effect should be weak or even disabled if it
complicates equilibrium establishment unnecessarily.

The priority is a stable, interpretable baseline equilibrium, not immediate
ecological maximalism.

## Initial condition and equilibration

### Initial prey state

Start from a simple low-abundance initial condition, for example

$$
N_0(x) = \eta_0 K(x),
\qquad 0 < \eta_0 \ll 1.
$$

This can be uniform across cells or include a tiny amount of deterministic
jitter if needed for symmetry breaking.

### Equilibrium definition

The module should run the prey-only dynamics forward until a numerical
equilibrium is reached.

Recommended convergence rule:

$$
\max_{x \in \mathcal{X}}
\left|
\frac{N_{t+1}(x) - N_t(x)}{\max(1, N_t(x))}
\right|
< \varepsilon
$$

for a fixed number of consecutive steps.

The implementation spec can set concrete values such as:

- $\varepsilon = 10^{-6}$,
- consecutive steps required: `20`,
- maximum iteration cap: large enough to fail clearly if convergence is not
  achieved.

### Required output object

The baseline module should return at least:

- domain metadata,
- cell coordinates and adjacency,
- suitability surface `S(x)`,
- carrying capacity surface `K(x)`,
- final equilibrium abundance surface `N^*(x)`,
- optional equilibrium occupancy surface
  $$
  O^*(x) = \mathbf{1}[N^*(x) > \tau_{\mathrm{occ}}],
  $$
- convergence diagnostics.

This object becomes the canonical starting state for the next module.

## Module boundaries

This first module stops **before**:

- predator arrival,
- predation ramping,
- extirpation-time generation,
- observation noise,
- response-only TX estimation,
- parameter recovery.

Those belong to later modules.

## Why this is the right first step

This baseline module creates a truth object that is known in every relevant
sense:

- known geometry,
- known habitat,
- known dynamical rules,
- known parameter values,
- known equilibrium abundance.

That makes it the right anchor for later tests of:

- simulated predator introduction,
- extirpation timing generation,
- incomplete/noisy observation,
- reconstructed `TX`,
- summary statistics,
- parameter recovery under degraded data.

## Tests and acceptance criteria

The module should not be considered complete until the following are true.

### Structural checks

- The domain contains exactly `625` cells.
- Adjacency is valid and symmetric under the chosen graph representation.
- The suitability surface is fully finite and bounded in `[0,1]`.
- The carrying-capacity surface is fully finite and strictly positive.

### Dynamical checks

- The prey-only simulation converges to equilibrium under the declared stopping
  rule.
- The final equilibrium abundance surface is fully finite and non-negative.
- The equilibrium is spatially non-uniform.
- The equilibrium is not degenerate:
  neither near-zero everywhere nor saturated identically everywhere.

### Reproducibility checks

- Running the module twice with the same configuration gives identical outputs.
- All parameters used to generate `S(x)`, `K(x)`, and `N^*(x)` are recorded.

### Visual checks

At minimum, the module should emit plots for:

- the suitability surface,
- the carrying-capacity surface,
- the equilibrium abundance surface,
- optional equilibrium occupancy.

## Explicit recommendation on hexes

Hexes should be treated as a **planned variant**, not the initial blocker.

The right near-term sequence is:

1. implement `synth-small` on a square `25 x 25` lattice,
2. keep the spatial layer graph-based and tessellation-agnostic,
3. once the baseline module is stable, add a hex-domain sibling benchmark if we
   want to test isotropy and topology sensitivity.

If the user later decides that hexes are a hard scientific commitment rather
than a nice-to-have, then the correct response will be:

- retain the module design in this spec,
- switch only the domain geometry and adjacency backend,
- avoid any square-specific convolution assumptions in the high-level API.

## Instruction to `spat`

The next implementation task after this spec should build the `synth-small`
baseline module only. It should not attempt predator introduction, observation
generation, or recovery analysis in the same step.

The implementation should aim to produce one clean baseline truth object:

$$
\left(\mathcal{X}, S, K, N^*\right),
$$

with auditable configuration and tests, ready for the next synthetic module.
