#!/usr/bin/env python3
"""Build the synth-medium recoverability-target observation-design review pack."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.medium import (
    DEFAULT_SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_DIR,
    build_synth_medium_recoverability_target_observation_design,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_DIR,
        help="Directory for emitted synth-medium recoverability-target artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_medium_recoverability_target_observation_design()
    written = result.write_artifacts(args.output_dir)
    summary = result.summary_dict()

    print("Synth-medium recoverability-target observation-design review pack complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Baseline regime: {summary['baseline_regime_id']}")
    print(f"Baseline primary rule: {summary['baseline_rule_id']}")
    print(f"Candidate regime count: {summary['candidate_regime_count']}")
    print(f"Rule count: {summary['rule_count']}")
    print(f"Best field-plausible regime: {summary['best_field_plausible_regime_id']}")
    print(f"Best field-plausible rule: {summary['best_field_plausible_rule_id']}")
    print(f"Best field-plausible finite recall: {summary['best_field_plausible_finite_recall']}")
    print(
        "Best field-plausible survey records: "
        f"{summary['best_field_plausible_survey_record_count']}"
    )
    print(
        "Best field-plausible false negatives: "
        f"{summary['best_field_plausible_false_negative_count']}"
    )
    print(f"Lowest-effort ready regime: {summary['lowest_effort_ready_regime_id']}")
    print(f"Lowest-effort ready rule: {summary['lowest_effort_ready_rule_id']}")
    print(
        f"Lowest-effort ready survey records: {summary['lowest_effort_ready_survey_record_count']}"
    )
    print(f"Ceiling finite recall: {summary['ceiling_finite_recall']}")
    print(f"Ceiling false negatives: {summary['ceiling_false_negative_count']}")
    print(f"Ceiling survey records: {summary['ceiling_survey_record_count']}")
    print(f"Decision recommendation: {result.recommendation_class}")
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
