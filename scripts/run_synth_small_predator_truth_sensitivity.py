from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small.sensitivity import run_predator_truth_sensitivity


def main() -> None:
    parser = ArgumentParser(
        description="Run the synth-small predator-truth deterministic sensitivity sweep."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/synth_small_predator_truth_sensitivity"),
        help="Directory for emitted sensitivity/readiness artifacts.",
    )
    args = parser.parse_args()

    result = run_predator_truth_sensitivity(args.output_dir)
    print(
        "Sensitivity sweep complete: "
        f"candidates={len(result.rows)} "
        f"default={result.default_row.readiness_classification} "
        f"best={result.best_row.label}:{result.best_row.readiness_classification} "
        f"output_dir={result.output_dir}"
    )


if __name__ == "__main__":
    main()
