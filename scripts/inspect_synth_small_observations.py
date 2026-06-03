from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import inspect_synth_small_observation_artifacts


def main() -> None:
    parser = ArgumentParser(
        description="Inspect an existing synth-small response-only observation bundle."
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("artifacts/synth_small_observations"),
        help="Path to an existing synth-small observation artifact directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional override for the inspection output directory.",
    )
    args = parser.parse_args()

    result = inspect_synth_small_observation_artifacts(
        args.artifact_dir,
        output_dir=args.output_dir,
    )
    smoke_status = "passed" if result.recoverability_smoke["passed"] else "failed"
    status = "passed" if result.passed else "failed"
    print(
        "Observation inspection "
        f"{status}: verification={result.verification_path} "
        f"smoke={smoke_status} "
        f"output_dir={result.output_dir}"
    )
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
