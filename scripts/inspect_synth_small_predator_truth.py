from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small.predator_inspect import inspect_synth_small_predator_truth_artifacts


def main() -> None:
    parser = ArgumentParser(
        description="Inspect an existing synth-small predator-truth artifact bundle."
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("artifacts/synth_small_predator_truth"),
        help="Path to an existing synth-small predator-truth artifact directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional override for the inspection output directory.",
    )
    args = parser.parse_args()

    result = inspect_synth_small_predator_truth_artifacts(
        args.artifact_dir,
        output_dir=args.output_dir,
    )
    status = "passed" if result.passed else "failed"
    print(
        "Predator-truth inspection "
        f"{status}: verification={result.verification_path} "
        f"output_dir={result.output_dir} warnings={len(result.scientific_warnings)}"
    )
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
