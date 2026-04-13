# Theory

## Purpose

This document lays out the mathematical theory that underpins the initial
`spatext` modelling program. It is intended to be the scientific anchor for the
simulation and inference machinery that will be implemented in this repository.

It is distilled from the working ideas already operationalised in
`exdyn-sandbox`, but rewritten here as a clean theory document. The aim is not
to preserve every legacy implementation detail. The aim is to make the model
class, inferential target, and logic of validation explicit.

## Central proposition

We observe a biological response, not the driver itself. The central
proposition of the project is:

> A spatially spreading extinction driver can sometimes be inferred from
> response-only evidence if we model the latent driver-arrival process, the prey
> response dynamics, the observation process, and the extirpation estimator
> explicitly, and if we validate the entire workflow under synthetic truth.

The key inferential object is not raw abundance, which is usually unobserved,
but an extirpation-time surface:

$$
T_X(x) = \text{time of extirpation at location } x.
$$

This is related to a hypothesised driver-arrival surface:

$$
T_P(x) = \text{time of driver arrival at location } x.
$$

The theory therefore has five linked layers:

1. a latent driver-arrival process,
2. a latent prey-dynamics process,
3. a first-passage definition of extirpation,
4. an observation process that converts latent dynamics into response-only data,
5. a summary-based inference layer comparing observed and simulated
   extirpation patterns.

## Scope

The initial `spatext` theory is deliberately narrower than "all possible causes
of decline". It focuses on the following model class:

- the driver spreads through space and time,
- the prey responds through local decline and extirpation,
- the main data product is a reconstructed `T_X(x)` surface from sparse
  response observations,
- inference is pattern-oriented rather than full-state likelihood-based,
- validation is synthetic-first.

The first applied case remains mink and water vole, but the theory is written
for the more general class of response-only spatial extirpation problems.

## Notation

Let:

- $x \in \mathcal{X}$ denote a spatial cell or location,
- $t \in \{t_0, t_1, \ldots, t_T\}$ denote discrete time, typically annual,
- $\mathcal{M} \subseteq \mathcal{X}$ denote the analysis mask,
- $g(x)$ denote a spatial grouping function, for example region or segment,
- $N_t(x)$ denote latent prey abundance,
- $T_P(x)$ denote the nominal arrival time of the driver,
- $T_P^\delta(x)$ denote the arrival time after optional regional offsets,
- $P_t(x)$ denote driver pressure or predation intensity at time $t$,
- $Y_t(x)$ denote observed response counts or detections,
- $T_X^{\mathrm{true}}(x)$ denote latent extirpation time,
- $T_X^{\mathrm{obs}}(x)$ denote extirpation time reconstructed from
  observations,
- $\theta$ denote the model parameter vector.

The initial parameter vector is expected to include quantities of the form

$$
\theta =
\left(
r_{\max},
A,
K_0,
\alpha,
\mu,
c,
h,
\gamma,
r_{\mathrm{ramp}},
\rho_0,
\delta
\right),
$$

where:

- $r_{\max}$ is intrinsic growth strength,
- $A$ is the Allee-scale parameter,
- $K_0$ is carrying capacity,
- $\alpha$ is dispersal share,
- $\mu$ is the dispersal scale,
- $c$ and $h$ are predation-response parameters,
- $\gamma$ shapes the post-arrival predation ramp,
- $r_{\mathrm{ramp}}$ is ramp duration,
- $\rho_0$ is pre-arrival leakage,
- $\delta$ collects regional arrival-time offsets.

## 1. Driver-arrival surface

The driver is represented first by an arrival-time surface:

$$
T_P : \mathcal{X} \to \mathbb{R} \cup \{\mathrm{NA}\}.
$$

In the focal case this is the mink arrival year surface. In general it is the
time at which the hypothesised spreading driver reaches each location.

### 1.1 Regional timing offsets

Observed arrival surfaces may be biased by detection lag or regional reporting
effects. The sandbox introduced region-level timing offsets $\delta_g$, which
shift the driver-arrival surface by group:

$$
T_P^\delta(x) = \mathrm{clip}\!\left(T_P(x) - \delta_{g(x)},\; t_0,\; t_T\right).
$$

These offsets are not free nuisance knobs. They are part of the inferential
model and must remain bounded and, when used in real-data fitting,
regularised.

## 2. Time-varying driver pressure

Arrival time is not itself the force acting on the prey. The force acting on
the prey is a time-varying pressure field derived from arrival.

Let

$$
\Delta_t(x) = t - T_P^\delta(x).
$$

Define a logistic ramp

$$
\sigma(z) = \frac{1}{1 + e^{-z}},
$$

with ramp steepness

$$
k_{\mathrm{ramp}} = \frac{6}{r_{\mathrm{ramp}}}.
$$

The baseline post-arrival ramp used in the sandbox is:

$$
\widetilde{P}_t(x) =
\begin{cases}
\rho_0, & \Delta_t(x) < 0, \\
\max\!\left\{\rho_0,\;
\min\!\left(1,\; 0.2 + 0.8\,\sigma\!\left(k_{\mathrm{ramp}}
\left[\Delta_t(x) - \frac{r_{\mathrm{ramp}}}{2}\right]\right)\right)\right\},
& \Delta_t(x) \ge 0.
\end{cases}
$$

This yields a bounded ramp from a pre-arrival leakage level $\rho_0$ toward a
nominal full-pressure state after arrival.

The final pressure field allows both scalar and spatial modulation:

$$
P_t(x) =
a(x)\,\widetilde{P}_t(x)^\gamma,
$$

where

$$
a(x) = s_{\mathrm{pred}} \, m(x).
$$

Here $s_{\mathrm{pred}}$ is a global predation scale and $m(x)$ is an optional
spatial multiplier, for example a riparian suitability weight.

## 3. Latent prey dynamics

The prey process is modelled in discrete time on the same spatial domain.

### 3.1 Local demographic update

The most general local update encoded in the sandbox can be written as

$$
\widetilde{N}_{t+1}(x)
=
N_t(x)\,
\exp\!\Big(
r_{\max}\,f_S(S(x))\,A_{\mathrm{allee}}(N_t(x))
\left[1 - \frac{N_t(x)}{K_t(x)}\right]
- M_t(x)
- d
\Big),
$$

where:

$$
A_{\mathrm{allee}}(N) = 1 - \frac{A}{N + A},
$$

$$
K_t(x) = K_0 \left[1 - \beta_H H_t(x)\right],
$$

$$
f_S(S) = \frac{1}{1 + \exp\!\left[-k_S (S - s_0)\right]}.
$$

Interpretation:

- $A_{\mathrm{allee}}(N)$ introduces a low-density penalty,
- $f_S(S)$ maps habitat or suitability into a growth multiplier,
- $K_t(x)$ permits a habitat-pressure term $H_t(x)$ to reduce carrying
  capacity,
- $d$ is background loss.

### 3.2 Predation mortality term

The sandbox supports at least two standard predation-response forms.

Type II:

$$
M_t(x) =
c \, \frac{P_t(x)\,N_t(x)}{h + N_t(x)}.
$$

Type III:

$$
M_t(x) =
c \, \frac{P_t(x)\,N_t(x)^2}{h^2 + N_t(x)^2}.
$$

The initial `spatext` implementation should support both forms, even if one is
chosen as the default in early papers.

### 3.3 Dispersal operator

After the local update, abundance is redistributed by dispersal:

$$
N_{t+1}(x) =
(1 - \alpha)\,\widetilde{N}_{t+1}(x)
+
\alpha\,(\mathcal{K}_\mu \widetilde{N}_{t+1})(x),
$$

where $\alpha \in [0,1]$ is the dispersal share and $\mathcal{K}_\mu$ is a
dispersal operator with scale $\mu$.

Two computational representations are already justified by the sandbox and
should remain part of the theory:

1. a convolutional operator on a regular grid,
2. a graph operator on valid land cells or habitat-connected cells.

The graph form is especially useful when the analysis mask is sparse or
topologically constrained.

### 3.4 Initial condition

The sandbox typically initialised abundance at a low but positive fraction of
carrying capacity, for example

$$
N_{t_0}(x) \approx 0.1\,K_0.
$$

This is a modelling convenience, not a deep scientific commitment. The theory
requires only that the initial condition be explicitly stated and consistent
between simulation and synthetic validation.

### 3.5 First implementation simplification

The streaming TX-only engine in the sandbox used the special case

$$
S(x) = 1, \qquad H_t(x) = 0, \qquad K_t(x) = K_0,
$$

so that habitat enters only through masking or predation scaling, not through a
time-varying carrying-capacity term. That simplification is acceptable for the
first implementation of `spatext`, provided the more general theory remains the
reference frame.

## 4. Latent extirpation time

The latent response target is the first-passage time below an extinction
threshold.

Define the latent threshold

$$
\tau_{\mathrm{true}}(x) =
\min\!\left(\phi K_0,\; \rho N_{t_0}(x)\right),
$$

where $\phi$ is a carrying-capacity fraction and $\rho$ is a relative-to-initial
fraction.

Then define latent extirpation time by

$$
T_X^{\mathrm{true}}(x)
=
\inf\left\{
t > t_0 :
N_{t-1}(x) > \tau_{\mathrm{true}}(x)
\;\wedge\;
N_t(x) \le \tau_{\mathrm{true}}(x)
\right\}.
$$

This is a first-passage definition. It is important for two reasons:

1. it converts a full abundance trajectory into the response surface that is
   actually inferable,
2. it aligns the synthetic truth target with the observation-derived target.

This alignment is one of the most important inheritances from `exdyn-sandbox`
and should be preserved.

## 5. Observation model

The project is response-only. We therefore need an explicit map from latent
abundance dynamics to sparse observations.

### 5.1 Counts-mode observation model

The primary observation model should be cell-year counts:

$$
Y_t(x) \sim \mathrm{Poisson}\!\left(q\,E_t(x)\,N_t(x)\right),
$$

where:

- $q$ is an observation-rate parameter,
- $E_t(x)$ is an effort or accessibility multiplier.

The sandbox used a static access surface based on distance from grid edges and
normalised it to mean 1. For `spatext`, this should be treated as one possible
parametric family for $E_t(x)$, not as the only admissible effort model.

### 5.2 Point-mode observation model

For completeness, the sandbox also allowed a point-sampling representation.
This can be written as:

$$
M_t \sim \mathrm{Poisson}\!\left(q \sum_{x \in \mathcal{M}} E_t(x) N_t(x)\right),
$$

with individual observations allocated conditionally by

$$
\Pr(X_{t,m} = x \mid M_t)
\propto
E_t(x)\,N_t(x).
$$

This is useful as a conceptual bridge to presence-only records, but counts mode
should remain the default synthetic observation layer because it is closer to
the inferential target and much cheaper computationally.

### 5.3 Additional observation degradation

Synthetic experiments may also include:

- missing observation years,
- random dropout in reconstructed extirpation times,
- effort-normalised response series.

These are not separate ecological mechanisms. They are part of the observation
model and must be varied explicitly in synthetic validation.

## 6. Observation-derived extirpation estimator

The real inferential object is not latent abundance but reconstructed
extirpation timing from sparse response records.

For each cell $x$, let $C_t(x)$ denote the observed count or an
effort-normalised index. Let $\bar{C}_t(x)$ denote a centred moving-average
smoothed version of that series.

### 6.1 First active year and baseline

Let

$$
t_{\mathrm{first}}(x) = \min\{t : \bar{C}_t(x) > 0\}.
$$

If the series has too few active years after first detection, no extirpation
time is assigned.

Given a baseline window of length $w_B$, define

$$
B(x) =
\mathrm{median}\left\{
\bar{C}_t(x) :
t_{\mathrm{first}}(x) \le t < t_{\mathrm{first}}(x) + w_B
\right\}.
$$

### 6.2 Threshold modes

The sandbox settled on an explicit threshold-mode distinction that should carry
into `spatext`.

For raw count-scale series:

$$
\tau_{\mathrm{obs}}(x) =
\max\left(1,\left\lfloor \eta\,B(x) \right\rfloor\right).
$$

For effort-normalised or continuous indices:

$$
\tau_{\mathrm{obs}}(x) =
\eta\,B(x).
$$

Here $\eta \in (0,1)$ is a drop fraction.

### 6.3 Hold-rule first-passage estimator

Let $h$ denote the required hold duration. Then the observation-derived
extirpation time is

$$
T_X^{\mathrm{obs}}(x)
=
\inf\Big\{
t > t_{\mathrm{first}}(x) :
\bar{C}_s(x) \le \tau_{\mathrm{obs}}(x)
\;\forall s \in \{t,\ldots,t+h-1\},
\;
\exists u < t \text{ such that } \bar{C}_u(x) > \tau_{\mathrm{obs}}(x),
\;
\bar{C}_v(x) \le \tau_{\mathrm{obs}}(x)
\;\forall v \ge t+h
\Big\}.
$$

This definition matters. It prevents extirpation from being declared on the
basis of a single-year dip and ensures that synthetic realistic mode and real
data use the same response-side estimator.

## 7. Response-side summary statistics

Inference is not performed directly on all cells simultaneously. Instead, the
observed and simulated extirpation patterns are compared through a compact
summary vector.

The default response-oriented summary should be of the form

$$
S(T_X, T_P)
=
\left(
g,\;
\pi,\;
c,\;
\ell,\;
s_\ell,\;
r^2_{XP},\;
R,\;
v,\;
r^2_v,\;
\bar{T}_X,\;
s_X,\;
C(b_1),\ldots,C(b_J)
\right).
$$

The terms are defined as follows.

### 7.1 Coverage

Coverage of finite extirpation timing over locations with finite driver arrival:

$$
c =
\frac{
\sum_{x \in \mathcal{M}}
\mathbf{1}\!\left[T_X(x) \text{ finite} \wedge T_P(x) \text{ finite}\right]
}{
\sum_{x \in \mathcal{M}}
\mathbf{1}\!\left[T_P(x) \text{ finite}\right]
}.
$$

### 7.2 Lag summaries

For the paired set

$$
\mathcal{A} =
\{x \in \mathcal{M} : T_X(x) \text{ finite},\; T_P(x) \text{ finite}\},
$$

define

$$
\ell = \frac{1}{|\mathcal{A}|}\sum_{x \in \mathcal{A}} \left(T_X(x) - T_P(x)\right),
$$

$$
s_\ell = \mathrm{sd}\left(T_X(x) - T_P(x) : x \in \mathcal{A}\right).
$$

### 7.3 Arrival-extirpation coupling

The sandbox used squared Pearson correlation as a simple arrival-alignment
diagnostic:

$$
r^2_{XP} =
\mathrm{cor}\!\left(
\{T_X(x)\}_{x \in \mathcal{A}},
\{T_P(x)\}_{x \in \mathcal{A}}
\right)^2.
$$

This is not a full likelihood and should not be interpreted as one. It is a
pattern-alignment statistic.

### 7.4 Front-plane geometry

Fit a plane to the extirpation surface:

$$
T_X(x) = a + b_1 r(x) + b_2 c(x) + \varepsilon_x,
$$

where $r(x)$ and $c(x)$ are row and column coordinates.

Then define front-gradient magnitude

$$
g = \sqrt{b_1^2 + b_2^2}.
$$

The sandbox also used a weighted principal-axis ratio $\pi$ to capture
elongation of the extirpation pattern.

### 7.5 Orientation concentration

Using local gradients of the extirpation surface, define unit direction vectors
$u_x$ for cells with valid local orientation. Then

$$
R = \frac{\left\| \sum_x u_x \right\|}{n_u},
$$

where $n_u$ is the number of valid local direction vectors.

This is a directional concentration statistic:

- $R \approx 1$ means strong coherence,
- $R \approx 0$ means diffuse or conflicting orientations.

### 7.6 Response-side front speed

Given a dominant direction vector $d$, project locations onto that axis:

$$
z(x) = \langle s(x), d \rangle,
$$

where $s(x)$ is the spatial coordinate vector of cell $x$.

Fit

$$
T_X(x) = a + \beta z(x) + \varepsilon_x.
$$

Then define an effective front speed by

$$
v = \frac{1}{\beta},
$$

with an associated $r^2_v$ from the same regression.

### 7.7 Coverage curve

For chosen breakpoints $b_1 < \cdots < b_J$, define

$$
C(b_j) =
\frac{
\sum_{x \in \mathcal{M}}
\mathbf{1}\!\left[T_P(x) \text{ finite} \wedge T_X(x) \text{ finite}
\wedge T_X(x) \le b_j\right]
}{
\sum_{x \in \mathcal{M}}
\mathbf{1}\!\left[T_P(x) \text{ finite}\right]
}.
$$

The sandbox showed that these breakpoints should sometimes be chosen by
quantiles of `TX` rather than evenly over calendar years, because fixed-year
breaks can become uninformative when extirpation is late and concentrated.

## 8. Screening objective

The initial inference architecture is deliberately modular:

1. a screen stage over many parameter draws,
2. a summary-based ABC refinement stage.

### 8.1 Compatibility gates

The screen first checks whether a simulated pattern is even vaguely compatible
with the observed one. In the sandbox this meant threshold rules such as

$$
r^2_{XP,\mathrm{sim}} \ge r^2_{\min},
$$

$$
\ell_{\min} \le \ell_{\mathrm{sim}} \le \ell_{\max},
$$

$$
c_{\mathrm{sim}} \ge c_{\min}.
$$

These are not posterior statements. They are coarse admissibility gates.

### 8.2 Weighted gap loss

The basic screen loss can be written as

$$
L_{\mathrm{screen}}(\theta)
=
w_{r^2}\,\left|r^2_{XP,\mathrm{sim}} - r^2_{XP,\mathrm{obs}}\right|
+ w_{\ell}\,\psi\!\left(\ell_{\mathrm{sim}}\right)
+ w_c\,\left|c_{\mathrm{sim}} - c_{\mathrm{obs}}\right|
+ w_R\,\left|R_{\mathrm{sim}} - R_{\mathrm{obs}}\right|
+ w_C\,\mathrm{RMSE}\!\left(C_{\mathrm{sim}}, C_{\mathrm{obs}}\right),
$$

where $\psi(\ell)$ is a lag penalty equal to zero inside the acceptable lag
range and positive outside it.

This loss is a ranking device, not a generative likelihood.

## 9. Unit-consistent real-data loss

For real case studies, the sandbox moved away from mixing cell-level and
unit-level quantities inside one objective. That change should carry into
`spatext`.

Let $u$ denote an analysis unit, for example a segment or aggregated grid unit.
Define unit-level timings by a chosen aggregation rule, currently the median:

$$
\widetilde{T}_P(u) = \mathrm{median}\{T_P(x) : x \in u,\; T_P(x) \text{ finite}\},
$$

$$
\widetilde{T}_X^{\mathrm{obs}}(u) =
\mathrm{median}\{T_X^{\mathrm{obs}}(x) : x \in u,\; T_X^{\mathrm{obs}}(x) \text{ finite}\},
$$

$$
\widetilde{T}_X^{\mathrm{sim}}(u) =
\mathrm{median}\{T_X^{\mathrm{sim}}(x) : x \in u,\; T_X^{\mathrm{sim}}(x) \text{ finite}\}.
$$

The same paired statistics and coverage curves are then computed on these unit
timing tables rather than by mixing scales.

### 9.1 Delta regularisation

When regional offsets are used, they must be penalised:

$$
\Omega(\delta)
=
\lambda_{\mathrm{mag}}\,
\frac{1}{G}
\sum_{g=1}^{G} \delta_g^2
+
\lambda_{\mathrm{tv}}\,
\frac{1}{|E|}
\sum_{(g,h) \in E} |\delta_g - \delta_h|,
$$

where $E$ is an adjacency set over regions or segments.

### 9.2 Real-data objective

The real-data objective therefore becomes

$$
L_{\mathrm{real}}(\theta)
=
w_{r^2}\,\left|r^2_{\mathrm{sim}} - r^2_{\mathrm{obs}}\right|
+ w_{\ell}\,\psi\!\left(\ell_{\mathrm{sim}}\right)
+ w_c\,\left|c_{\mathrm{sim}} - c_{\mathrm{obs}}\right|
+ w_R\,\left|R_{\mathrm{sim}} - R_{\mathrm{obs}}\right|
+ w_C\,\mathrm{RMSE}\!\left(C_{\mathrm{sim}}, C_{\mathrm{obs}}\right)
+ w_\delta\,\Omega(\delta).
$$

This is still not a full likelihood, but it is scientifically cleaner than a
mixed-scale objective.

## 10. ABC refinement

After screening, refinement is performed in summary space.

Let

$$
S^{\mathrm{obs}} = S(T_X^\dagger, T_P),
$$

where $T_X^\dagger$ is the target surface for the current mode:

- ideal mode: $T_X^\dagger = T_X^{\mathrm{true}}$,
- realistic mode: $T_X^\dagger = T_X^{\mathrm{obs}}$.

For a simulated draw $\theta$, let

$$
S^{\mathrm{sim}}(\theta) = S(T_X^{\mathrm{sim}}(\theta), T_P^\delta(\theta)).
$$

Given scale factors $s_k > 0$ for summary components, define the core ABC
distance

$$
d_{\mathrm{core}}(\theta)
=
\left[
\sum_{k \in \mathcal{K}_{\mathrm{finite}}}
\left(
\frac{S^{\mathrm{sim}}_k(\theta) - S^{\mathrm{obs}}_k}{s_k}
\right)^2
\right]^{1/2}.
$$

The sandbox also enforced two important rules:

1. required summary components must be finite, otherwise the draw is rejected,
2. optional missing components can incur an additive penalty.

Writing $m_{\mathrm{opt}}(\theta)$ for the number of missing optional metrics,
the full distance is

$$
d(\theta) = d_{\mathrm{core}}(\theta) + \lambda_{\mathrm{miss}}\,m_{\mathrm{opt}}(\theta).
$$

The ABC acceptance rule is then

$$
\theta \in \mathcal{A}_\varepsilon
\quad\Longleftrightarrow\quad
d(\theta) \le \varepsilon.
$$

The initial implementation may use rejection ABC, optionally seeded by a
Latin-hypercube scan and followed by a tighter second pass.

## 11. Synthetic twin as the scientific safeguard

The theory is not complete without validation logic.

The synthetic twin should generate data under known truth $\theta^\star$:

1. construct $T_P^{\delta^\star}(x)$,
2. simulate latent abundance trajectories $N_t(x)$,
3. derive $T_X^{\mathrm{true}}(x)$,
4. apply the observation model to generate response-only data,
5. reconstruct $T_X^{\mathrm{obs}}(x)$ using the same estimator used for real
   data,
6. run screen and ABC against either $T_X^{\mathrm{true}}$ or
   $T_X^{\mathrm{obs}}$.

This creates two distinct validation questions:

### 11.1 Ideal identifiability

Can the inference machinery recover meaningful information when extirpation
timing itself is known?

### 11.2 Realistic identifiability

Can the same machinery recover information after observation noise and the TX
estimator have been imposed?

The difference between these two is scientifically important. If ideal mode
works but realistic mode fails, the issue is observation and reconstruction. If
both fail, the issue is deeper than observation alone.

## 12. What the theory does and does not claim

This theory does claim:

- that response-only extirpation inference can be posed coherently,
- that the extirpation surface is a defensible response target,
- that the driver-arrival surface can be related to that target through a
  mechanistic spatiotemporal model,
- that validation must occur under synthetic truth before real-data claims are
  interpreted.

This theory does not claim:

- that every ecological mechanism is represented,
- that the weighted-gap objective is a full probabilistic likelihood,
- that identifiability is guaranteed in realistic data,
- that failure to fit a real case implies the underlying ecological hypothesis
  is false.

Failure may instead reflect sparse arrival information, weak response signal,
inadequate analysis units, missing mechanisms, or some combination of these.

## 13. Consequences for `spatext`

This theory implies a natural module structure for the new repository:

- `arrival`: construct and manipulate $T_P(x)$ and $T_P^\delta(x)$
- `pressure`: map arrival surfaces into $P_t(x)$
- `dynamics`: local update and dispersal operators for $N_t(x)$
- `tx`: latent first-passage extirpation definitions
- `observe`: observation models for counts and points
- `estimate`: reconstruct $T_X^{\mathrm{obs}}(x)$ from response-only data
- `summaries`: compute $S(T_X, T_P)$
- `screen`: run ranking and compatibility filters
- `abc`: run summary-space posterior approximation
- `synthetic`: generate and evaluate synthetic twins

That modular decomposition is not incidental. It is the implementation
consequence of the theory above and should guide how simulation work is built in
`spatext`.
