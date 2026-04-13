from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small.inspect import inspect_synth_small_artifacts


def main() -> None:
    parser = ArgumentParser(description="Inspect an existing synth-small baseline artifact bundle.")
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        required=True,
        help="Path to an existing synth-small baseline artifact directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional override for the inspection output directory.",
    )
    args = parser.parse_args()

    result = inspect_synth_small_artifacts(args.artifact_dir, output_dir=args.output_dir)
    status = "passed" if result.passed else "failed"
    print(
        "Inspection "
        f"{status}: verification={result.verification_path} "
        f"output_dir={result.output_dir}"
    )
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
