# Log

## 2026-06-14 - Orchestrator Packet

Barry approved moving beyond `synth-small` after Goal 016 showed that
response-observable timing and finite-support rules carry some signal but do
not restore compatibility. Barry emphasized that `synth-small` was worthwhile
and should eventually be catalogued for the paper, but that manuscript work is
far downstream because the project must still cover both synthetic work and
the real-world mink-vole case study in Britain.

Barry requested a split between landscape design and spread simulation:

- Goal 017 should generate an acceptable `synth-medium` landscape plus visual
  and audit-table review artifacts.
- Goal 018, only after Barry approves the Goal 017 landscape, should simulate
  predator spread and prey impact across that approved landscape.

The orchestrator created this Goal 017 packet for `mink`. The goal asks for a
deterministic `synth-medium` landscape design review pack with impassable
water/barrier cells, low-quality matrix, higher-quality patches, corridors,
spatial aggregation, multiple frontier/source zones, audit tables, and SVG
visuals for human sanity checking.

No implementation, validation run, commit, push, predator spread simulation,
prey dynamics, observation modelling, inference, real-data work, or
publication work was performed by the orchestrator.

## 2026-06-14 - Action Implementation Checkpoint

`mink` confirmed the action repo was on
`codex/spatext-goal017-synth-medium-landscape-review...origin/main` at the
Goal 016 commit `fdd865b`, with only the untracked Goal 017 packet present
before implementation work.

Read:

- `AGENTS.md`
- `README.md`
- `spec/problem_statement.md`
- `spec/theory.md`
- `spec/report_log.md` headings
- `spec/synth_small_baseline.md`
- `spec/synth_small_predator_truth.md`
- `spec/synth_small_observations.md`
- `spec/synth_small_response_observable_timing_rule_screen.md`
- `src/spatext/spatial.py`
- `src/spatext/synth/small/baseline.py`
- `src/spatext/synth/small/predator.py`
- current synth-small tests and CLI surfaces relevant to artifact-writing style

Implemented a deterministic synth-medium landscape review surface:

- `spec/synth_medium_landscape.md`
- `src/spatext/synth/medium/landscape.py`
- `src/spatext/synth/medium/__init__.py`
- `scripts/build_synth_medium_landscape.py`
- `tests/test_synth_medium_landscape.py`

The focused RED check was run before implementation:

```bash
uv run pytest tests/test_synth_medium_landscape.py --no-cov
```

It failed as expected because `spatext.synth.medium` did not yet exist.

The initial CLI smoke wrote `17` ignored files under
`artifacts/synth_medium_landscape/` with default dimensions `72 x 84`,
`6048` cells, `5225` passable cells, `823` water cells, `6` high-quality
patches, `5` corridors, and `3` western source zones. Verification passed and
all passable cells were source-reachable.

No predator spread, prey dynamics, observation model, extirpation
reconstruction, summary-vector or compatibility-screen change, response-rule
adoption, ABC, POM, likelihood, MCMC, posterior, parameter recovery, fitting,
real-data analysis, broad sweep, remote compute, commit, or push was performed.
