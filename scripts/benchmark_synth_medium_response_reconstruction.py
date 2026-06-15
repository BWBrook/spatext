#!/usr/bin/env python3
"""Build the synth-medium response reconstruction benchmark review pack."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.medium import (
    DEFAULT_SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_OUTPUT_DIR,
    build_synth_medium_response_reconstruction_benchmark,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_OUTPUT_DIR,
        help="Directory for emitted synth-medium response-reconstruction artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_medium_response_reconstruction_benchmark()
    written = result.write_artifacts(args.output_dir)
    summary = result.summary_dict()

    print("Synth-medium response reconstruction benchmark complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Selected default regime: {result.config.selected_default_regime_id}")
    print(f"Rule count: {len(result.rules)}")
    print(f"Primary default rule: {summary['primary_default_rule_id']}")
    print(f"Default finite recall: {summary['default_best_finite_recall']}")
    print(f"Default median absolute error: {summary['default_best_median_absolute_error']}")
    print(f"Recommendation: {result.recommendation_class}")
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
