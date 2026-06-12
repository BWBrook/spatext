"""Build the synthetic-only synth-small summary-vector bundle."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import build_synth_small_summary_vector


def main() -> None:
    parser = ArgumentParser(description="Build synth-small summary-vector artifacts.")
    parser.add_argument(
        "--reconstruction-dir",
        type=Path,
        default=Path("artifacts/synth_small_extirpation_reconstruction"),
        help="Path to existing synth-small extirpation reconstruction artifacts.",
    )
    parser.add_argument(
        "--observation-dir",
        type=Path,
        default=Path("artifacts/synth_small_observations"),
        help="Path to existing synth-small observation artifacts with evaluation truth.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/synth_small_summary_vector"),
        help="Output path for summary-vector artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_small_summary_vector(
        reconstruction_dir=args.reconstruction_dir,
        observation_dir=args.observation_dir,
    )
    written = result.write_artifacts(args.output_dir)
    mode_summaries = result.mode_summary["mode_summaries"]
    print(
        "Summary vector complete: "
        f"files={len(written)} "
        f"ideal_targets={mode_summaries['ideal_true']['finite_target_count']} "
        f"observed_targets={mode_summaries['realistic_observed']['finite_target_count']} "
        f"passed={result.passed} "
        f"output_dir={args.output_dir}"
    )
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
