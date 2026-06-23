#!/usr/bin/env python3
"""Build the synth-medium observation-design counterfactual screen."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from spatext.synth.medium import (
    DEFAULT_SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_OUTPUT_DIR,
    build_synth_medium_observation_design_counterfactual_screen,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_OUTPUT_DIR,
        help="Directory for emitted synth-medium observation-design counterfactual artifacts.",
    )
    args = parser.parse_args()

    result = build_synth_medium_observation_design_counterfactual_screen()
    written = result.write_artifacts(args.output_dir)
    summary = result.summary_dict()

    print("Synth-medium observation-design counterfactual screen complete")
    print(f"Output directory: {args.output_dir}")
    print(f"Baseline regime: {summary['baseline_regime_id']}")
    print(f"Baseline primary rule: {summary['baseline_rule_id']}")
    print(f"Regime count: {summary['regime_count']}")
    print(f"Rule count: {summary['rule_count']}")
    print(f"Best plausible regime: {summary['best_plausible_regime_id']}")
    print(f"Best plausible rule: {summary['best_plausible_rule_id']}")
    print(f"Best plausible finite recall: {summary['best_plausible_finite_recall']}")
    print(f"Best plausible false negatives: {summary['best_plausible_false_negative_count']}")
    print(f"Ceiling finite recall: {summary['ceiling_finite_recall']}")
    print(f"Ceiling false negatives: {summary['ceiling_false_negative_count']}")
    print(f"Decision recommendation: {result.recommendation_class}")
    print(f"Wrote {len(written)} files")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
