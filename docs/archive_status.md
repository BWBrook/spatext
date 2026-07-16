# SpatExt Archive Status

Date: 2026-07-16

## Transition decision

`spatext` is leaving active scientific development. Canonical `main` may
receive one documentation-only archival administration commit recording this
transition; after that, the repository is a read-only laboratory notebook and
parts catalogue. No further scientific implementation or goal development is
authorized here.

## Accepted scientific endpoint

Goal 022, **Synth-Medium Recoverability-Target Observation-Design Review
Pack**, at commit `53462d0365babf2c8070714a930f69b4071af276` is the last
accepted scientific checkpoint. Its acceptance remains bounded to the
synthetic review-pack claims recorded at that commit; it does not adopt a
production observation design, reconstruction rule, fitting workflow, or
real-data inference.

The planned final tag on archival `main` is `spatext-exploratory-final`. That
tag will identify the documentation-complete archive state and must not be
read as extending scientific acceptance beyond Goal 022 and commit
`53462d0365babf2c8070714a930f69b4071af276`.

## Unfinished Goal 023

The unfinished Goal 023 work is preserved on
`archive/goal023-latent-response-observation-gate`. It is **BLOCKED, NOT
ACCEPTED, and NOT PUBLISHED**. Its final independent rereview records three
unresolved Important findings. No Goal 023 production run, production
artifact, holdout, or publication was authorized or completed.

## Successor programme

Active work will move to the private
[`BWBrook/latent-landscapes`](https://github.com/BWBrook/latent-landscapes)
repository, with its canonical local checkout planned at
`/Users/bwbrook/papers/latent-landscapes`.

## Reusable record

The accepted repository state through Goal 022 remains reusable as historical,
auditable source material:

- the scientific framing and mathematical theory;
- accepted synthetic landscape, spread-impact, observation, reconstruction,
  and recoverability diagnostics;
- their specifications, tests, and provenance records; and
- modular implementation and review patterns that can be evaluated afresh in
  the successor programme.

Goal 023's archival branch remains reusable only as blocked design,
implementation, and review evidence. It is not an accepted scientific or
production component.

## Intentionally superseded

The following are intentionally superseded:

- `spatext` as the active home for new scientific implementation;
- any continuation from Goal 022 into Goal 023 within this repository;
- Goal 023's unfinished implementation as an accepted or publishable result;
  and
- any interpretation of the synthetic observation-design work as a deployed
  production design or real-data inference workflow.
