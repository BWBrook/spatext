#!/usr/bin/env python3
"""Run the synth-small observation-support counterfactual screen."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import (
    DEFAULT_COMPATIBILITY_SCREEN_OUTPUT_DIR,
    DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
    DEFAULT_OBSERVATION_DIR,
    DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR,
    DEFAULT_RECONSTRUCTION_DIR,
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    DEFAULT_SUMMARY_VECTOR_OUTPUT_DIR,
    build_synth_small_observation_support_counterfactual_screen,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
        help="Path to the response-screen evaluation artifact bundle.",
    )
    parser.add_argument(
        "--reconstruction-dir",
        type=Path,
        default=DEFAULT_RECONSTRUCTION_DIR,
        help="Path to the extirpation-reconstruction artifact bundle.",
    )
    parser.add_argument(
        "--observation-dir",
        type=Path,
        default=DEFAULT_OBSERVATION_DIR,
        help="Path to the synth-small observation artifact bundle.",
    )
    parser.add_argument(
        "--false-negative-audit-dir",
        type=Path,
        default=DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
        help="Path to the Goal 012 false-negative audit bundle.",
    )
    parser.add_argument(
        "--summary-vector-dir",
        type=Path,
        default=DEFAULT_SUMMARY_VECTOR_OUTPUT_DIR,
        help="Path to the Goal 009 summary-vector bridge bundle.",
    )
    parser.add_argument(
        "--compatibility-screen-dir",
        type=Path,
        default=DEFAULT_COMPATIBILITY_SCREEN_OUTPUT_DIR,
        help="Path to the Goal 010 compatibility-screen bridge bundle.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR,
        help="Directory for Goal 013 counterfactual-screen artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_small_observation_support_counterfactual_screen(
        evaluation_dir=args.evaluation_dir,
        reconstruction_dir=args.reconstruction_dir,
        observation_dir=args.observation_dir,
        false_negative_audit_dir=args.false_negative_audit_dir,
        summary_vector_dir=args.summary_vector_dir,
        compatibility_screen_dir=args.compatibility_screen_dir,
    )
    written = result.write_artifacts(args.output_dir)
    summary_by_id = {row.scenario_id: row for row in result.reconstruction_summary_rows}
    status_quo = summary_by_id["status_quo"]
    best_loss = min(
        result.reconstruction_summary_rows,
        key=lambda row: (
            row.top_total_weighted_loss if row.top_total_weighted_loss is not None else float("inf")
        ),
    )
    restored = [
        row.scenario_id
        for row in result.reconstruction_summary_rows
        if row.restores_status_quo_finite_drop
    ]

    print("Observation-support counterfactual screen complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Status quo finite targets: {status_quo.finite_target_count}")
    print(f"False negatives audited: {result.false_negative_count}")
    print(f"Recommendation: {result.recommendation['recommendation_class']}")
    print(f"Finite target restored by: {', '.join(restored) if restored else 'none'}")
    print(
        "Best loss scenario: "
        f"{best_loss.scenario_id} "
        f"({best_loss.top_candidate_label}, {best_loss.top_compatibility_class})"
    )
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
