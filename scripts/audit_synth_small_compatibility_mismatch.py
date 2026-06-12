#!/usr/bin/env python3
"""Audit the synth-small realistic-observed compatibility mismatch."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import (
    DEFAULT_COMPATIBILITY_MISMATCH_AUDIT_OUTPUT_DIR,
    DEFAULT_COMPATIBILITY_SCREEN_OUTPUT_DIR,
    DEFAULT_COMPATIBILITY_SCREEN_TARGET_DIR,
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    build_synth_small_compatibility_mismatch_audit,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary-vector-dir",
        type=Path,
        default=DEFAULT_COMPATIBILITY_SCREEN_TARGET_DIR,
        help="Path to the Goal 009 summary-vector artifact bundle.",
    )
    parser.add_argument(
        "--compatibility-screen-dir",
        type=Path,
        default=DEFAULT_COMPATIBILITY_SCREEN_OUTPUT_DIR,
        help="Path to the Goal 010 compatibility-screen artifact bundle.",
    )
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
        help="Path to the Goal 008 response-screen evaluation artifact bundle.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_COMPATIBILITY_MISMATCH_AUDIT_OUTPUT_DIR,
        help="Directory for Goal 011 mismatch-audit artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_small_compatibility_mismatch_audit(
        summary_vector_dir=args.summary_vector_dir,
        compatibility_screen_dir=args.compatibility_screen_dir,
        evaluation_dir=args.evaluation_dir,
    )
    written = result.write_artifacts(args.output_dir)
    bridge = result.evaluation_bridge_summary
    recommendation = result.recommendation

    print("Compatibility mismatch audit complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Top target mode: {result.config.top_target_mode}")
    print(f"Top candidate: {result.top_candidate_label}")
    print(f"Recommendation: {recommendation['recommendation_class']}")
    print(f"Finite-target drop: {bridge['finite_target_drop']}")
    print(f"False negatives: {bridge['false_negative_count']}")
    print(f"Bridge class: {bridge['bridge_class']}")
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
