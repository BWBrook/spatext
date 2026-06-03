"""Run the response-only synth-small extirpation reconstruction."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import (
    ReconstructionConfig,
    build_synth_small_extirpation_reconstruction,
)


def main() -> None:
    parser = ArgumentParser(description="Build response-only extirpation reconstruction artifacts.")
    parser.add_argument(
        "--observation-dir",
        type=Path,
        default=Path("artifacts/synth_small_observations"),
        help="Path to existing synth-small observation artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/synth_small_extirpation_reconstruction"),
        help="Output path for reconstruction artifacts.",
    )
    parser.add_argument(
        "--min-final-absence-run",
        type=int,
        default=2,
        help="Minimum length of final absence tail required to call observed extinction.",
    )
    args = parser.parse_args()

    config = ReconstructionConfig(
        observation_artifact_dir=str(args.observation_dir),
        min_final_absence_run=args.min_final_absence_run,
    )
    result = build_synth_small_extirpation_reconstruction(
        args.observation_dir,
        config=config,
    )
    written = result.write_artifacts(args.output_dir)

    print(
        "Reconstruction complete: "
        f"files={len(written)} "
        f"sites={len(result.site_rows)} "
        f"survey_times={len(result.time_summary_rows)} "
        f"passed={result.passed} "
        f"output_dir={args.output_dir}"
    )


if __name__ == "__main__":
    main()
