"""Inspect an existing response-only extirpation reconstruction bundle."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import inspect_synth_small_extirpation_reconstruction_artifacts


def main() -> None:
    parser = ArgumentParser(description="Inspect an existing reconstruction artifact bundle.")
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("artifacts/synth_small_extirpation_reconstruction"),
        help="Path to an existing reconstruction artifact directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional override for inspection output directory.",
    )
    args = parser.parse_args()

    result = inspect_synth_small_extirpation_reconstruction_artifacts(
        args.artifact_dir,
        output_dir=args.output_dir,
    )
    status = "passed" if result.passed else "failed"
    print(
        "Reconstruction inspection "
        f"{status}: verification={result.verification_path} output_dir={result.output_dir}"
    )
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
