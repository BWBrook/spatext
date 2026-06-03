from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.small import build_synth_small_observations


def main() -> None:
    parser = ArgumentParser(
        description="Build the synth-small first response-only observation bundle."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/synth_small_observations"),
        help="Directory for emitted observation artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_small_observations()
    written = result.write_artifacts(args.output_dir)
    print(
        "Observation bundle complete: "
        f"files={len(written)} "
        f"visits={len(result.visit_rows)} "
        f"observations={len(result.observation_rows)} "
        f"seed={result.config.survey.seed} "
        f"output_dir={args.output_dir}"
    )


if __name__ == "__main__":
    main()
