from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import build_synth_small_baseline


def main() -> None:
    parser = ArgumentParser(description="Build the synth-small baseline truth object.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/synth_small_baseline"),
        help="Directory for emitted baseline artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_small_baseline()
    written = result.write_artifacts(args.output_dir)
    print(f"Wrote {len(written)} artifacts to {args.output_dir}")


if __name__ == "__main__":
    main()
