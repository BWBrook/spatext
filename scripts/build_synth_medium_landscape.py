#!/usr/bin/env python3
"""Build the synth-medium landscape design review pack."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.medium import (
    DEFAULT_SYNTH_MEDIUM_LANDSCAPE_OUTPUT_DIR,
    build_synth_medium_landscape,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_SYNTH_MEDIUM_LANDSCAPE_OUTPUT_DIR,
        help="Directory for emitted synth-medium landscape artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_medium_landscape()
    written = result.write_artifacts(args.output_dir)
    summary = result.summary_dict()
    status = "passed" if result.passed else "failed"

    print("Synth-medium landscape review pack complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Dimensions: {result.config.rows} x {result.config.cols}")
    print(f"Cells: {summary['cell_count']}")
    print(f"Passable cells: {summary['passable_cell_count']}")
    print(f"Water cells: {summary['water_cell_count']}")
    print(f"Source zones: {summary['source_zone_count']}")
    print(f"Patches: {summary['patch_count']}")
    print(f"Corridors: {summary['corridor_count']}")
    print(f"Verification: {status}")
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
