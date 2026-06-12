#!/usr/bin/env python3
"""Audit synth-small response-screen false-negative mechanisms."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import (
    DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
    DEFAULT_FALSE_NEGATIVE_MISMATCH_AUDIT_DIR,
    DEFAULT_OBSERVATION_DIR,
    DEFAULT_RECONSTRUCTION_DIR,
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    build_synth_small_false_negative_mechanism_audit,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
        help="Path to the Goal 008 response-screen evaluation artifact bundle.",
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
        "--mismatch-audit-dir",
        type=Path,
        default=DEFAULT_FALSE_NEGATIVE_MISMATCH_AUDIT_DIR,
        help="Path to the Goal 011 compatibility-mismatch audit bundle.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
        help="Directory for Goal 012 false-negative audit artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_small_false_negative_mechanism_audit(
        evaluation_dir=args.evaluation_dir,
        reconstruction_dir=args.reconstruction_dir,
        observation_dir=args.observation_dir,
        mismatch_audit_dir=args.mismatch_audit_dir,
    )
    written = result.write_artifacts(args.output_dir)
    dominant = result.mechanism_rows[0]
    recommendation = result.recommendation

    print("False-negative mechanism audit complete")
    print(f"Output directory: {args.output_dir}")
    print(f"False negatives audited: {result.false_negative_count}")
    print(f"Recommendation: {recommendation['recommendation_class']}")
    print(f"Dominant mechanism: {dominant.primary_mechanism} ({dominant.false_negative_count})")
    print(
        "Strongest region signal: "
        f"{recommendation['strongest_region_signal']['group']} "
        f"({recommendation['strongest_region_signal']['false_negative_count']})"
    )
    print(
        "Strongest front-band signal: "
        f"{recommendation['strongest_front_band_signal']['group']} "
        f"({recommendation['strongest_front_band_signal']['false_negative_count']})"
    )
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
