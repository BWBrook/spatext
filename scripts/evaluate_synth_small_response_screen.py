"""Run the synthetic-only evaluation audit for synth-small response-screen artifacts."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import evaluate_synth_small_response_screen


def main() -> None:
    parser = ArgumentParser(description="Evaluate synth-small response-screen artifacts.")
    parser.add_argument(
        "--screen-dir",
        type=Path,
        default=Path("artifacts/synth_small_response_screen"),
        help="Path to existing response-screen artifacts.",
    )
    parser.add_argument(
        "--reconstruction-dir",
        type=Path,
        default=Path("artifacts/synth_small_extirpation_reconstruction"),
        help="Path to existing extirpation reconstruction artifacts.",
    )
    parser.add_argument(
        "--observation-dir",
        type=Path,
        default=Path("artifacts/synth_small_observations"),
        help="Path to existing observation artifacts containing evaluation truth.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/synth_small_response_screen/evaluation"),
        help="Output path for synthetic-only evaluation artifacts.",
    )
    args = parser.parse_args()

    result = evaluate_synth_small_response_screen(
        screen_dir=args.screen_dir,
        reconstruction_dir=args.reconstruction_dir,
        observation_dir=args.observation_dir,
    )
    written = result.write_artifacts(args.output_dir)
    matrix = result.summary["classification"]["confusion_matrix"]
    print(
        "Response screen evaluation complete: "
        f"files={len(written)} "
        f"decision={result.summary['screen_decision']} "
        f"tp={matrix['tp']} fp={matrix['fp']} tn={matrix['tn']} fn={matrix['fn']} "
        f"passed={result.passed} "
        f"output_dir={args.output_dir}"
    )
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
