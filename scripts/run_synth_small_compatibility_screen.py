#!/usr/bin/env python3
"""Build the synth-small synthetic compatibility-screen bundle."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import (
    DEFAULT_COMPATIBILITY_SCREEN_OUTPUT_DIR,
    DEFAULT_COMPATIBILITY_SCREEN_TARGET_DIR,
    build_synth_small_compatibility_screen,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target-dir",
        default=str(DEFAULT_COMPATIBILITY_SCREEN_TARGET_DIR),
        help="Path to the Goal 009 summary-vector target bundle.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_COMPATIBILITY_SCREEN_OUTPUT_DIR),
        help="Directory for compatibility-screen artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_small_compatibility_screen(target_dir=Path(args.target_dir))
    written = result.write_artifacts(args.output_dir)

    print("Compatibility screen complete")
    print(f"Output directory: {Path(args.output_dir)}")
    print(f"Candidate count: {len(result.config.candidates)}")
    print(f"Primary target mode: {result.config.primary_target_mode}")
    for mode in result.config.target_modes:
        top = next(row for row in result.ranking_rows if row.target_mode == mode and row.rank == 1)
        loss = "NA" if top.total_weighted_loss is None else f"{top.total_weighted_loss:.12g}"
        print(f"Top {mode}: {top.candidate.label} ({top.compatibility_class}, loss={loss})")
    print(f"Wrote {len(written)} files")


if __name__ == "__main__":
    main()
