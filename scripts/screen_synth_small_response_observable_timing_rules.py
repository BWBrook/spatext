#!/usr/bin/env python3
"""Run the synth-small response-observable timing-rule screen."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import (
    DEFAULT_COMPATIBILITY_SCREEN_OUTPUT_DIR,
    DEFAULT_OBSERVATION_DIR,
    DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR,
    DEFAULT_RECONSTRUCTION_DIR,
    DEFAULT_RESPONSE_OBSERVABLE_TIMING_RULE_SCREEN_OUTPUT_DIR,
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    DEFAULT_SUMMARY_VECTOR_OUTPUT_DIR,
    DEFAULT_TARGET_TIME_ERROR_ANATOMY_OUTPUT_DIR,
    DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR,
    build_synth_small_response_observable_timing_rule_screen,
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
        "--observation-support-counterfactual-dir",
        type=Path,
        default=DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR,
        help="Path to the Goal 013 observation-support counterfactual bundle.",
    )
    parser.add_argument(
        "--target-timing-residual-dir",
        type=Path,
        default=DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR,
        help="Path to the Goal 014 target-timing residual-decomposition bundle.",
    )
    parser.add_argument(
        "--target-time-error-anatomy-dir",
        type=Path,
        default=DEFAULT_TARGET_TIME_ERROR_ANATOMY_OUTPUT_DIR,
        help="Path to the Goal 015 target-time error anatomy bundle.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_RESPONSE_OBSERVABLE_TIMING_RULE_SCREEN_OUTPUT_DIR,
        help="Directory for Goal 016 response-observable timing-rule screen artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_small_response_observable_timing_rule_screen(
        observation_dir=args.observation_dir,
        reconstruction_dir=args.reconstruction_dir,
        evaluation_dir=args.evaluation_dir,
        summary_vector_dir=args.summary_vector_dir,
        compatibility_screen_dir=args.compatibility_screen_dir,
        observation_support_counterfactual_dir=args.observation_support_counterfactual_dir,
        target_timing_residual_dir=args.target_timing_residual_dir,
        target_time_error_anatomy_dir=args.target_time_error_anatomy_dir,
    )
    written = result.write_artifacts(args.output_dir)
    best = result.recommendation["best_eligible_response_observable_rule"]

    print("Response-observable timing-rule screen complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Rules evaluated: {len(result.rule_definitions)}")
    eligible_count = result.recommendation["eligible_response_observable_rule_count"]
    print(f"Eligible response-observable rules: {eligible_count}")
    print(f"Best eligible rule: {best['target_rule_id']}")
    print(f"Best eligible class: {best['compatibility_class']}")
    print(f"Recommendation: {result.recommendation['recommendation_class']}")
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
