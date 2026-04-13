# Problem Statement

## Purpose of this document

This document defines the scientific case for `spatext`. It is not an
implementation plan and it is not a restatement of the legacy sandbox. Its role
is to explain, in clean form, what scientific problem the new repository exists
to solve, what the first paper is trying to show, and what kind of modelling
and inference workflow is required to support that claim.

## The scientific problem

Many ecological declines unfold in space and time, but the drivers of those
declines are often only partially observed. In particular, there are important
cases where:

- the putative driver spreads as a front or invasion process,
- the biological response is a local extinction or extirpation process,
- direct measurements of the driver are sparse, noisy, biased, or missing, and
- the response is observed only through irregular presence-only records.

This creates a difficult inference problem. We want to reconstruct
spatiotemporal extinction dynamics and learn about the underlying driver
process, but the data we actually possess are indirect, incomplete, and shaped
by observation effort.

The central challenge is therefore:

> Can we infer meaningful features of a spatially spreading extinction driver
> from response-only evidence, while distinguishing genuine ecological signal
> from artefacts introduced by sparse, biased observation?

## Why this matters

This is not just a technical modelling exercise. Many systems of conservation
concern are known primarily through patchy detection histories, and ecological
decisions are often made under exactly these information constraints. A useful
framework would allow us to:

- reconstruct when and where extirpation likely occurred,
- test whether a hypothesised spreading driver is sufficient to explain the
  observed pattern,
- identify which parameters are genuinely learnable and which are weakly
  identified,
- treat failure to recover signal as an informative scientific result rather
  than as a hidden modelling inconvenience.

The scientific value of the project is therefore twofold:

1. as a general method for response-only spatiotemporal inference, and
2. as an applied case study in predator-driven prey extirpation.

## Core scientific idea

The guiding idea is to infer extinction dynamics from a reconstructed
extirpation-time surface, rather than from rich abundance data that usually do
not exist in real applications.

The workflow starts with a response variable:

- `TX(x)`: the time of extirpation at location `x`, inferred from observations.

This response is then related to a hypothesised spreading driver:

- `TP(x)`: the arrival time of the driver at location `x`.

The scientific claim is not that every latent ecological detail can be
recovered. The claim is narrower and more defensible:

- some large-scale features of the driver-response system may be recoverable
  from response-only information,
- recoverability depends strongly on observation quality and spatial coverage,
- these limits can and should be quantified explicitly.

## First-paper aims

The first paper built from `spatext` should pursue four linked aims.

### Aim 1: Define a coherent response-only inference framework

Build a scientifically interpretable framework for reconstructing spatial
extirpation dynamics from sparse observations, with clear definitions of:

- driver arrival,
- extirpation timing,
- observation process,
- summary statistics,
- inferential targets,
- failure conditions.

### Aim 2: Validate the framework under synthetic truth

Use synthetic experiments to separate:

- ideal identifiability, where true extirpation timing is known, and
- realistic identifiability, where extirpation timing must be reconstructed
  after observation noise and sampling bias.

This synthetic benchmark is the main scientific safeguard. No substantive
real-data claim should be made unless the benchmark first shows what is
recoverable, what is weakly identified, and where inference collapses.

### Aim 3: Apply the framework to a focal ecological case

Use the mink-water-vole system as the first substantive case study:

- invasive American mink (*Neovison vison*) as the spreading predator,
- water vole (*Arvicola amphibius*) as the responding prey,
- Great Britain / Ireland as the current spatial domain.

The purpose of this case study is not to force a positive fit. It is to ask
whether the observed extirpation pattern is consistent with a predator-front
mechanism at the available resolution, and if not, whether the failure is best
explained by low information, missing mechanisms, or both.

### Aim 4: Produce an inference workflow that is scientifically auditable

The project must make it easy to see:

- what assumptions were made,
- what data were used,
- what quantities were inferred,
- what gates were passed or failed,
- which conclusions are supported and which are not.

In other words, the end product is not only a fitted model, but an auditable map
of where inference is and is not justified.

## Sketch of the method

The working method can be described in five steps.

### 1. Represent the driver as a spatial arrival process

Construct a driver-arrival surface `TP(x)` that encodes when the hypothesised
driver reaches each location. In the focal case, this is the mink arrival year
surface.

### 2. Represent the response as extirpation timing

Infer an extirpation-time surface `TX(x)` from presence-only records using an
explicit first-passage rule. This is the key response-only object that links the
data to the process model.

### 3. Simulate a process-explicit driver-response system

Use a spatially explicit model of local dynamics, dispersal, and driver impact
to generate extirpation timing under alternative parameter settings. The model
must be capable of scaling to large domains without relying on impractical
high-memory representations.

### 4. Compare observed and simulated patterns through summary-based inference

Rather than fit every cell directly, compare observed and simulated
extirpation-time patterns using summary features that capture:

- coverage,
- lag structure,
- spatial geometry,
- front orientation and speed,
- cumulative coverage curves and related descriptors.

Inference can then proceed through staged screening and posterior refinement,
provided the objective remains scientifically coherent and transparent.

### 5. Validate with synthetic benchmarks before interpreting real data

The same machinery used on real data must first be exercised against synthetic
truth. This benchmark should quantify:

- parameter recovery,
- posterior predictive adequacy,
- weak-identifiability regimes,
- failure regimes caused by sparse arrivals, sparse observations, or poor
  overlap between driver and response information.

## What success looks like

For the first paper, success does not require a triumphant real-data fit.
Success means the project can support the following claims clearly and honestly:

1. A clean response-only framework for spatial extirpation inference has been
   defined.
2. The framework has been validated against synthetic truth, including explicit
   identifiability limits and failure regimes.
3. The real mink-water-vole case has been analysed under those same standards.
4. A negative or equivocal real-data result is treated as scientifically
   meaningful if the benchmark and diagnostics show why the information content
   is insufficient.

## Scope boundaries for the new repository

To keep `spatext` clean, the new repository should be built around the core
scientific spine above and should avoid inheriting avoidable sandbox baggage.

In particular, the new repo should privilege:

- clear separation between scientific specification and implementation,
- modular components for process model, observation model, extirpation
  estimator, summaries, inference, and diagnostics,
- explicit synthetic-first validation,
- reproducibility and gate-driven interpretation from the outset.

It should avoid treating exploratory legacy structure as authoritative simply
because it existed in the sandbox.

## Working thesis for the builder agent

The new repository exists to support a paper built around this proposition:

> Spatial extinction dynamics can sometimes be inferred from response-only
> observations, but only if the workflow explicitly models observation
> limitations, validates recoverability under synthetic truth, and treats
> low-information failure as part of the scientific result.

This proposition should anchor future specs, architecture decisions, and
implementation tasks in `spatext`.
