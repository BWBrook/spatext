# Plan

1. Read repo-local guidance and the published Goal 017-021 specs/modules.
2. Write a focused Goal 022 test contract first.
3. Implement the review-pack module using existing Goal 019 observation and
   Goal 020 reconstruction APIs.
4. Add a small deterministic candidate-regime set with baseline, six
   field-plausible candidates, and a diagnostic ceiling.
5. Emit review tables, verification JSON, Markdown report, and readable SVG
   visuals.
6. Update README, AGENTS, spec/report log, exports, and CLI wiring.
7. Regenerate ignored artifacts with the CLI and run the validation ladder.
8. Wake the SpatExt orchestrator with outcomes, validation evidence, artifact
   handling, and boundary confirmation.

## Design Guardrails

- Field-plausible candidates may use landscape strata, scheduled survey waves,
  observed detection history, and final-absence support gaps.
- Field-plausible candidates must not use hidden truth to decide where or when
  to survey.
- Hidden truth is allowed only in synthetic audit tables and recommendation
  checks after response-only observations and reconstructions are built.
- The diagnostic ceiling remains a reference, never a field-readiness claim.
