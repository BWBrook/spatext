#!/usr/bin/env python3
"""Build the synth-medium observation-design review pack."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.medium import (
    DEFAULT_SYNTH_MEDIUM_OBSERVATION_DESIGN_OUTPUT_DIR,
    build_synth_medium_observation_design_review_pack,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_SYNTH_MEDIUM_OBSERVATION_DESIGN_OUTPUT_DIR,
        help="Directory for emitted synth-medium observation-design artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_medium_observation_design_review_pack()
    written = result.write_artifacts(args.output_dir)
    summary = result.summary_dict()

    print("Synth-medium observation-design review pack complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Selected default regime: {result.config.selected_default_regime_id}")
    print(f"Regime count: {len(result.regime_summary_rows)}")
    print(f"Default survey records: {summary['default_survey_record_count']}")
    print(f"Default false negatives: {summary['default_false_negative_count']}")
    print(f"Recommendation: {result.recommendation_class}")
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
