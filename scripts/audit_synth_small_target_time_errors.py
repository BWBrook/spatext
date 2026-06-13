#!/usr/bin/env python3
"""Run the synth-small target-time error anatomy audit."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import (
    DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
    DEFAULT_OBSERVATION_DIR,
    DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR,
    DEFAULT_RECONSTRUCTION_DIR,
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    DEFAULT_TARGET_TIME_ERROR_ANATOMY_OUTPUT_DIR,
    DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR,
    build_synth_small_target_time_error_anatomy_audit,
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
        "--target-timing-residual-dir",
        type=Path,
        default=DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR,
        help="Path to the Goal 014 target-timing residual-decomposition bundle.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_TARGET_TIME_ERROR_ANATOMY_OUTPUT_DIR,
        help="Directory for Goal 015 target-time error anatomy artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_small_target_time_error_anatomy_audit(
        observation_dir=args.observation_dir,
        reconstruction_dir=args.reconstruction_dir,
        evaluation_dir=args.evaluation_dir,
        false_negative_audit_dir=args.false_negative_audit_dir,
        observation_support_counterfactual_dir=args.observation_support_counterfactual_dir,
        target_timing_residual_dir=args.target_timing_residual_dir,
    )
    written = result.write_artifacts(args.output_dir)

    print("Target-time error anatomy audit complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Sites audited: {len(result.site_rows)}")
    print(f"True extirpated sites: {result.recommendation['true_extirpated_site_count']}")
    print(f"Recommendation: {result.recommendation['recommendation_class']}")
    print(
        "Dominant remaining error group: "
        f"{result.recommendation['dominant_remaining_error_group']['group']}"
    )
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
