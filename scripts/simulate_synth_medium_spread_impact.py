#!/usr/bin/env python3
"""Simulate the synth-medium spread-impact review pack."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.medium import (
    DEFAULT_SYNTH_MEDIUM_SPREAD_IMPACT_OUTPUT_DIR,
    build_synth_medium_spread_impact_review_pack,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_SYNTH_MEDIUM_SPREAD_IMPACT_OUTPUT_DIR,
        help="Directory for emitted synth-medium spread-impact review artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_medium_spread_impact_review_pack()
    written = result.write_artifacts(args.output_dir)
    summary = result.summary_dict()

    print("Synth-medium spread-impact review pack complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Selected parameter set: {result.selected_candidate.parameter_set_id}")
    print(f"Final colonized passable cells: {summary['final_colonized_passable_count']}")
    print(f"Finite prey extirpations: {summary['finite_prey_extirpation_count']}")
    print(f"Material source count: {summary['material_source_count']}")
    print(f"Recommendation: {result.recommendation_class}")
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
