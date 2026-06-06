"""Inspect an emitted synth-small response-screen artifact bundle."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import inspect_synth_small_response_screen_artifacts


def main() -> None:
    parser = ArgumentParser(description="Inspect existing response-screen artifacts.")
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("artifacts/synth_small_response_screen"),
        help="Path to an existing synth-small response-screen artifact directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional override for inspection output directory.",
    )
    args = parser.parse_args()

    result = inspect_synth_small_response_screen_artifacts(
        args.artifact_dir,
        output_dir=args.output_dir,
    )
    status = "passed" if result.passed else "failed"
    print(
        "Response screen inspection "
        f"{status}: verification={result.verification_path} output_dir={result.output_dir}"
    )
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
