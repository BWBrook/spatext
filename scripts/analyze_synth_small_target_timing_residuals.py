#!/usr/bin/env python3
"""Run the synth-small target-timing residual decomposition diagnostic."""

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
    DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR,
    build_synth_small_target_timing_residual_decomposition,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--observation-dir",
        type=Path,
        default=DEFAULT_OBSERVATION_DIR,
        help="Path to the synth-small observation artifact bundle.",
    )
    parser.add_argument(
        "--reconstruction-dir",
        type=Path,
        default=DEFAULT_RECONSTRUCTION_DIR,
        help="Path to the extirpation-reconstruction artifact bundle.",
    )
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
        help="Path to the response-screen evaluation artifact bundle.",
    )
    parser.add_argument(
        "--false-negative-audit-dir",
        type=Path,
        default=DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
        help="Path to the Goal 012 false-negative audit bundle.",
    )
    parser.add_argument(
        "--observation-support-counterfactual-dir",
        type=Path,
        default=DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR,
        help="Path to the Goal 013 observation-support counterfactual bundle.",
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
        default=DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR,
        help="Directory for Goal 014 residual-decomposition artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_small_target_timing_residual_decomposition(
        observation_dir=args.observation_dir,
        reconstruction_dir=args.reconstruction_dir,
        evaluation_dir=args.evaluation_dir,
        false_negative_audit_dir=args.false_negative_audit_dir,
        observation_support_counterfactual_dir=args.observation_support_counterfactual_dir,
        summary_vector_dir=args.summary_vector_dir,
        compatibility_screen_dir=args.compatibility_screen_dir,
    )
    written = result.write_artifacts(args.output_dir)
    default_rankings = {
        row.target_mode: row for row in result.ranking_rows if row.candidate.label == "default"
    }
    restored = result.recommendation["compatibility_restored_by"]
    support_components = result.recommendation["dominant_goal013_support_floor_default_components"]

    print("Target-timing residual decomposition complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Transforms evaluated: {len(default_rankings)}")
    print(f"Goal 010 ideal true restored by: {', '.join(restored) if restored else 'none'}")
    print(f"Recommendation: {result.recommendation['recommendation_class']}")
    print(
        "Goal 013 support-floor default loss: "
        f"{default_rankings['goal013_support_floor'].total_weighted_loss:.12g}"
    )
    print(f"Dominant support-floor residual: {support_components[0]['component']}")
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
