# Goal 023 Integrated Amendment Execution Brief

Work in `/Users/bwbrook/.codex/worktrees/spatext/goal023`.

Read first and treat as exact requirements:

1. repo `AGENTS.md`;
2. current Goal 023 Goal/Plan/Runbook/spec/Log;
3. `.superpowers/sdd/integrated-contract-amendment-proposal.md` (SHA-256
   `ee367b6014bf823ffda2f406186179271a0f0e56ac955ea35ae6fb11c3bea15d`);
4. `.superpowers/sdd/task-2b-audit-fix-report.md`;
5. `.superpowers/sdd/task-2b-repair-rereview.md` (SHA-256
   `aa4da61aec534282ff8302b989a46bb1298cc0c8596b4b9af9efe42e08548306`).

## Accepted Input State

- Task 2b source: `701dd468219737d8885a2f52ef9e4cbb8965397277f6b9d1a4f3ebbfe72bc673`.
- Task 2b tests: `cb18204c6c78e9a0a1f049198f563b131cd3ee8d84793d1dfa94a87d6f68b6aa`.
- Log: `2305` lines,
  `7a95d0ce27fb7ffa9e9ec77308659a68b243f79f986b85ecdb518d7365ebd5b6`.
- Task 2b independent rereview: `SUPPORTED`, no Critical/Important finding.
- Source receipt remains
  `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`.
- No Goal 023 artifact, config, receipt, calibration, or holdout exists.

## Ownership

Own only the coordinated amendment files required by the proposal:

- Goal 023 `Goal.md`, `Plan.md`, `Runbook.md`, and `Log.md`;
- `spec/synth_medium_latent_response_observation_recovery_gate.md`;
- `src/spatext/synth/medium/latent_response_observation_recovery.py`;
- `tests/test_synth_medium_latent_response_observation_recovery.py`;
- ignored `.superpowers/sdd/integrated-amendment-execution-report.md`.

Do not edit README, AGENTS, report_log, package exports, CLI, artifacts, config,
receipts, or any other file in this task.

## Required Sequence

1. Verify the bound input hashes and append-only Log prefix.
2. Append a Task 2b independent-acceptance child against the live parent.
3. Append the proposal's provenance-interpretation supersession child against
   the new live parent, preserving every earlier byte.
4. Add amendment RED tests before implementation/document changes. Record exact
   behavior-specific RED evidence. Tests use temporary non-holdout fixtures and
   must not construct, derive, preview, or inspect a Goal 023 holdout payload.
5. Apply the complete integrated proposal exactly: registry/truth firewall,
   fit identity and schemas, diagnostic-only latent metrics, total four-class
   decision contract, artifact/hash interfaces, provenance envelopes, pinned
   identity/footprint guards, nonmutating-failure disposition, fixture-only
   Task 3 smoke, and document patch map.
6. Run focused GREEN, observation/upstream regressions, Ruff, mypy, and
   `git diff --check`. Do not run live Task 3 scenarios, calibration, artifacts,
   config, freeze, or holdout.
7. Compute amended Goal/Plan/Runbook/spec/source/test hashes and append one
   `holdout_provenance_contract_amendment_v2` record against the live parent,
   with review status `PENDING` and holdout still blocked.
8. Write the complete evidence report.

## Stop Rules

Stop rather than improvise if the proposal conflicts with current accepted
Task 2b bytes, requires a scientific model/estimand/support/schedule/seed/gate
change, cannot preserve the Log prefix, or any test reaches holdout construction.
Do not stage, commit, push, or start Task 3.
