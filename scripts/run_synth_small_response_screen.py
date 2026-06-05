"""Run the tiny response-only synth-small screen."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from spatext.synth.small import build_response_only_screen


def main(argv: Sequence[str] | None = None) -> None:
    parser = ArgumentParser(description="Build response-only synth-small screen artifacts.")
    parser.add_argument(
        "--reconstruction-dir",
        type=Path,
        default=Path("artifacts/synth_small_extirpation_reconstruction"),
        help="Path to existing synth-small extirpation reconstruction artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/synth_small_response_screen"),
        help="Output path for response-only screen artifacts.",
    )
    args = parser.parse_args(argv)

    result = build_response_only_screen(args.reconstruction_dir)
    written = result.write_artifacts(args.output_dir)
    print(
        "Response screen complete: "
        f"files={len(written)} "
        f"sites={result.summary['site_count']} "
        f"decision={result.summary['screen_decision']} "
        f"passed={result.passed} "
        f"output_dir={args.output_dir}"
    )
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
