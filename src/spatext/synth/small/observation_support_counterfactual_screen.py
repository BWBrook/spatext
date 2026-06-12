"""Counterfactual observation-support screen for synth-small false negatives."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from csv import DictReader, writer
from dataclasses import dataclass, field
from json import dumps, loads
from math import isfinite
from os import PathLike
from pathlib import Path
from typing import Any

from .compatibility_screen import (
    CANDIDATE_SCORE_COLUMNS,
    MODE_RANKING_COLUMNS,
    CandidateScoreRow,
    CompatibilityScreenConfig,
    ModeRankingRow,
    build_candidate_profile,
    build_mode_rankings,
    scalar_value,
    score_candidate_against_target,
)
from .compatibility_screen import (
    DEFAULT_OUTPUT_DIR as DEFAULT_COMPATIBILITY_SCREEN_DIR,
)
from .false_negative_mechanism_audit import (
    DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
    DEFAULT_OBSERVATION_DIR,
    DEFAULT_RECONSTRUCTION_DIR,
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
)
from .observations import stringify_float
from .summary_vector import (
    DEFAULT_COVERAGE_BREAKPOINTS,
    CoverageCurveRow,
    SummaryComponentRow,
    SummaryVectorTargetRow,
    build_coverage_curve_rows,
    build_summary_component_rows,
)
from .summary_vector import (
    DEFAULT_OUTPUT_DIR as DEFAULT_SUMMARY_VECTOR_DIR,
)

DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR = (
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR / "observation_support_counterfactual"
)
OBSERVATION_SUPPORT_COUNTERFACTUAL_NAME = "synth-small-observation-support-counterfactual-screen"
OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_FILES = (
    "counterfactual_config.json",
    "scenario_definitions.csv",
    "site_counterfactual_resolution.csv",
    "scenario_reconstruction_summary.csv",
    "scenario_summary_vectors.csv",
    "scenario_compatibility_scores.csv",
    "scenario_rankings.csv",
    "recommendation.json",
    "verification.json",
    "report.md",
)
EVALUATION_REQUIRED_FILES = (
    "screen_evaluation_summary.json",
    "site_evaluation_audit.csv",
    "verification.json",
)
RECONSTRUCTION_REQUIRED_FILES = (
    "reconstruction_config.json",
    "site_reconstruction.csv",
    "verification.json",
)
OBSERVATION_REQUIRED_FILES = (
    "evaluation_truth.csv",
    "truth_reference.json",
)
FALSE_NEGATIVE_AUDIT_REQUIRED_FILES = (
    "false_negative_audit_config.json",
    "false_negative_site_audit.csv",
    "mechanism_summary.csv",
    "recommendation.json",
    "verification.json",
)
SUMMARY_VECTOR_BRIDGE_REQUIRED_FILES = (
    "mode_summary.json",
    "verification.json",
)
COMPATIBILITY_BRIDGE_REQUIRED_FILES = (
    "target_summary.json",
    "candidate_scores.csv",
    "mode_rankings.csv",
    "verification.json",
)
SCENARIO_IDS = (
    "status_quo",
    "truth_guided_absence_floor_all",
    "detection_blocker_respecting_floor",
    "late_followup_detection_blocker_respecting",
)
TIMING_GAP_MECHANISMS = (
    "no_post_extirpation_surveys",
    "late_extirpation_near_survey_horizon",
)
COUNTERFACTUAL_LABEL_KEYS = (
    "synthetic_only",
    "evaluation_only",
    "counterfactual_only",
    "not_formal_inference",
    "no_default_observation_design_change",
    "no_reconstruction_rule_change",
    "no_scoring_change",
)
SCENARIO_DEFINITION_COLUMNS = (
    "scenario_id",
    "label",
    "scenario_type",
    "synthetic_truth_guided",
    "diagnostic_upper_bound",
    "respects_post_extirpation_detections",
    "target_site_rule",
    "target_time_rule",
    "interpretation_limit",
)
SITE_COUNTERFACTUAL_COLUMNS = (
    "scenario_id",
    "site_id",
    "cell_id",
    "row",
    "col",
    "region",
    "front_band",
    "primary_mechanism",
    "post_extirpation_detection_count",
    "status_quo_observed_extirpation_time",
    "true_extirpation_time",
    "counterfactual_observed_extirpation_time",
    "resolved_false_negative",
    "resolution_rule",
    "unresolved_reason",
    "synthetic_support_start_time",
    "synthetic_support_survey_count",
)
SCENARIO_RECONSTRUCTION_SUMMARY_COLUMNS = (
    "scenario_id",
    "finite_target_count",
    "finite_target_fraction",
    "ideal_true_finite_target_count",
    "status_quo_finite_target_count",
    "false_negative_count",
    "resolved_false_negative_count",
    "remaining_false_negative_count",
    "post_extirpation_detection_blocker_count",
    "remaining_post_extirpation_detection_blocker_count",
    "top_candidate_label",
    "top_total_weighted_loss",
    "top_compatibility_class",
    "restores_status_quo_finite_drop",
    "restores_compatibility",
)
SCENARIO_SUMMARY_VECTOR_COLUMNS = (
    "scenario_id",
    "row_type",
    "metric",
    "value",
    "coverage_fraction",
    "finite_target_count",
    "missing_reason",
)
SCENARIO_COMPATIBILITY_SCORE_COLUMNS = ("scenario_id", *CANDIDATE_SCORE_COLUMNS[1:])
SCENARIO_RANKING_COLUMNS = ("scenario_id", *MODE_RANKING_COLUMNS[1:])


@dataclass(frozen=True, slots=True)
class CounterfactualScenario:
    scenario_id: str
    label: str
    scenario_type: str
    synthetic_truth_guided: bool
    diagnostic_upper_bound: bool
    respects_post_extirpation_detections: bool
    target_site_rule: str
    target_time_rule: str
    interpretation_limit: str
    applies_support: bool = True
    timing_gap_only: bool = False
    late_followup: bool = False

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.scenario_id,
            self.label,
            self.scenario_type,
            stringify_bool(self.synthetic_truth_guided),
            stringify_bool(self.diagnostic_upper_bound),
            stringify_bool(self.respects_post_extirpation_detections),
            self.target_site_rule,
            self.target_time_rule,
            self.interpretation_limit,
        )


def default_counterfactual_scenarios() -> tuple[CounterfactualScenario, ...]:
    """Return the small deterministic Goal 013 scenario set."""

    return (
        CounterfactualScenario(
            scenario_id="status_quo",
            label="Status quo",
            scenario_type="baseline",
            synthetic_truth_guided=False,
            diagnostic_upper_bound=False,
            respects_post_extirpation_detections=True,
            target_site_rule="existing observed extirpation targets only",
            target_time_rule="site_reconstruction.csv:observed_extirpation_time",
            interpretation_limit="baseline reconciliation only",
            applies_support=False,
        ),
        CounterfactualScenario(
            scenario_id="truth_guided_absence_floor_all",
            label="Truth-guided absence floor for all false negatives",
            scenario_type="diagnostic_upper_bound",
            synthetic_truth_guided=True,
            diagnostic_upper_bound=True,
            respects_post_extirpation_detections=False,
            target_site_rule="all false-negative sites",
            target_time_rule="true_extirpation_time + support_delay",
            interpretation_limit="upper bound, not an analyst-facing observation design",
        ),
        CounterfactualScenario(
            scenario_id="detection_blocker_respecting_floor",
            label="Detection-blocker-respecting absence floor",
            scenario_type="bounded_counterfactual",
            synthetic_truth_guided=True,
            diagnostic_upper_bound=False,
            respects_post_extirpation_detections=True,
            target_site_rule="false-negative sites without post-extirpation detections",
            target_time_rule="true_extirpation_time + support_delay",
            interpretation_limit="keeps post-extirpation detections as blockers",
        ),
        CounterfactualScenario(
            scenario_id="late_followup_detection_blocker_respecting",
            label="Late follow-up detection-blocker-respecting support",
            scenario_type="bounded_counterfactual",
            synthetic_truth_guided=True,
            diagnostic_upper_bound=False,
            respects_post_extirpation_detections=True,
            target_site_rule="timing-gap false negatives without post-extirpation detections",
            target_time_rule=(
                "max(true_extirpation_time + support_delay, last_survey_time + support_interval)"
            ),
            interpretation_limit="late follow-up diagnostic only",
            timing_gap_only=True,
            late_followup=True,
        ),
    )


@dataclass(frozen=True, slots=True)
class ObservationSupportCounterfactualConfig:
    evaluation_dir: str = str(DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR)
    reconstruction_dir: str = str(DEFAULT_RECONSTRUCTION_DIR)
    observation_dir: str = str(DEFAULT_OBSERVATION_DIR)
    false_negative_audit_dir: str = str(DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR)
    summary_vector_dir: str = str(DEFAULT_SUMMARY_VECTOR_DIR)
    compatibility_screen_dir: str = str(DEFAULT_COMPATIBILITY_SCREEN_DIR)
    scenarios: tuple[CounterfactualScenario, ...] = field(
        default_factory=default_counterfactual_scenarios
    )
    support_delay: float = 1.0
    support_interval: float = 4.0
    coverage_breakpoints: tuple[float, ...] = DEFAULT_COVERAGE_BREAKPOINTS
    compatibility_config: CompatibilityScreenConfig = field(
        default_factory=lambda: CompatibilityScreenConfig(
            target_modes=SCENARIO_IDS,
            primary_target_mode="status_quo",
        )
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            **counterfactual_labels(),
            "screen_name": OBSERVATION_SUPPORT_COUNTERFACTUAL_NAME,
            "evaluation_dir": self.evaluation_dir,
            "reconstruction_dir": self.reconstruction_dir,
            "observation_dir": self.observation_dir,
            "false_negative_audit_dir": self.false_negative_audit_dir,
            "summary_vector_dir": self.summary_vector_dir,
            "compatibility_screen_dir": self.compatibility_screen_dir,
            "scenario_ids": [scenario.scenario_id for scenario in self.scenarios],
            "support_delay": self.support_delay,
            "support_interval": self.support_interval,
            "coverage_breakpoints": list(self.coverage_breakpoints),
            "compatibility_contract": {
                "candidate_count": len(self.compatibility_config.candidates),
                "candidate_labels": [
                    candidate.label for candidate in self.compatibility_config.candidates
                ],
                "required_components": list(self.compatibility_config.required_components),
                "gap_settings": [
                    setting.to_dict() for setting in self.compatibility_config.gap_settings
                ],
                "compatible_loss_max": self.compatibility_config.compatible_loss_max,
                "borderline_loss_max": self.compatibility_config.borderline_loss_max,
            },
        }


@dataclass(frozen=True, slots=True)
class LoadedObservationSupportCounterfactualInputs:
    evaluation_dir: Path
    reconstruction_dir: Path
    observation_dir: Path
    false_negative_audit_dir: Path
    summary_vector_dir: Path
    compatibility_screen_dir: Path
    evaluation_summary: dict[str, Any]
    site_evaluation_rows: tuple[dict[str, str], ...]
    evaluation_verification: dict[str, Any]
    reconstruction_config: dict[str, Any]
    reconstruction_rows: tuple[dict[str, str], ...]
    reconstruction_verification: dict[str, Any]
    truth_rows: tuple[dict[str, str], ...]
    truth_reference: dict[str, Any]
    false_negative_config: dict[str, Any]
    false_negative_site_rows: tuple[dict[str, str], ...]
    false_negative_mechanism_rows: tuple[dict[str, str], ...]
    false_negative_recommendation: dict[str, Any]
    false_negative_verification: dict[str, Any]
    summary_vector_mode_summary: dict[str, Any]
    summary_vector_verification: dict[str, Any]
    compatibility_target_summary: dict[str, Any]
    compatibility_candidate_score_rows: tuple[dict[str, str], ...]
    compatibility_mode_ranking_rows: tuple[dict[str, str], ...]
    compatibility_verification: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SiteCounterfactualResolutionRow:
    scenario_id: str
    site_id: str
    cell_id: int
    row: int
    col: int
    region: str
    front_band: str
    primary_mechanism: str
    post_extirpation_detection_count: int
    status_quo_observed_extirpation_time: float | None
    true_extirpation_time: float
    counterfactual_observed_extirpation_time: float | None
    resolved_false_negative: bool
    resolution_rule: str
    unresolved_reason: str
    synthetic_support_start_time: float | None
    synthetic_support_survey_count: int

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.scenario_id,
            self.site_id,
            str(self.cell_id),
            str(self.row),
            str(self.col),
            self.region,
            self.front_band,
            self.primary_mechanism,
            str(self.post_extirpation_detection_count),
            stringify_optional_float(self.status_quo_observed_extirpation_time),
            stringify_float(self.true_extirpation_time),
            stringify_optional_float(self.counterfactual_observed_extirpation_time),
            stringify_bool(self.resolved_false_negative),
            self.resolution_rule,
            self.unresolved_reason,
            stringify_optional_float(self.synthetic_support_start_time),
            str(self.synthetic_support_survey_count),
        )


@dataclass(frozen=True, slots=True)
class ScenarioReconstructionSummaryRow:
    scenario_id: str
    finite_target_count: int
    finite_target_fraction: float
    ideal_true_finite_target_count: int
    status_quo_finite_target_count: int
    false_negative_count: int
    resolved_false_negative_count: int
    remaining_false_negative_count: int
    post_extirpation_detection_blocker_count: int
    remaining_post_extirpation_detection_blocker_count: int
    top_candidate_label: str
    top_total_weighted_loss: float | None
    top_compatibility_class: str
    restores_status_quo_finite_drop: bool
    restores_compatibility: bool

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.scenario_id,
            str(self.finite_target_count),
            stringify_float(self.finite_target_fraction),
            str(self.ideal_true_finite_target_count),
            str(self.status_quo_finite_target_count),
            str(self.false_negative_count),
            str(self.resolved_false_negative_count),
            str(self.remaining_false_negative_count),
            str(self.post_extirpation_detection_blocker_count),
            str(self.remaining_post_extirpation_detection_blocker_count),
            self.top_candidate_label,
            stringify_optional_float(self.top_total_weighted_loss),
            self.top_compatibility_class,
            stringify_bool(self.restores_status_quo_finite_drop),
            stringify_bool(self.restores_compatibility),
        )


@dataclass(frozen=True, slots=True)
class ScenarioSummaryVectorRow:
    scenario_id: str
    row_type: str
    metric: str
    value: str
    coverage_fraction: float | None = None
    finite_target_count: int | None = None
    missing_reason: str = ""

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.scenario_id,
            self.row_type,
            self.metric,
            self.value,
            stringify_optional_float(self.coverage_fraction),
            "" if self.finite_target_count is None else str(self.finite_target_count),
            self.missing_reason,
        )


@dataclass(frozen=True, slots=True)
class ObservationSupportCounterfactualCheck:
    name: str
    passed: bool
    message: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True, slots=True)
class SynthSmallObservationSupportCounterfactualResult:
    config: ObservationSupportCounterfactualConfig
    inputs: LoadedObservationSupportCounterfactualInputs
    site_rows: tuple[SiteCounterfactualResolutionRow, ...]
    summary_vector_rows: tuple[ScenarioSummaryVectorRow, ...]
    reconstruction_summary_rows: tuple[ScenarioReconstructionSummaryRow, ...]
    score_rows: tuple[CandidateScoreRow, ...]
    ranking_rows: tuple[ModeRankingRow, ...]
    recommendation: dict[str, Any]
    verification_checks: tuple[ObservationSupportCounterfactualCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    @property
    def false_negative_count(self) -> int:
        return len({row.site_id for row in self.site_rows})

    def config_payload(self) -> dict[str, Any]:
        status_quo_summary = summary_by_scenario(self.reconstruction_summary_rows)["status_quo"]
        return {
            **self.config.to_dict(),
            "scenario_count": len(self.config.scenarios),
            "false_negative_count": self.false_negative_count,
            "status_quo_finite_target_count": status_quo_summary.finite_target_count,
            "ideal_true_finite_target_count": status_quo_summary.ideal_true_finite_target_count,
            "min_final_absence_run": min_final_absence_run(self.inputs.reconstruction_config),
            "source_verifications": source_verifications(self.inputs),
            "bridge_reconciliation": bridge_reconciliation_payload(
                inputs=self.inputs,
                reconstruction_summary_rows=self.reconstruction_summary_rows,
            ),
        }

    def verification_payload(self) -> dict[str, Any]:
        return {
            **counterfactual_labels(),
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.verification_checks],
        }

    def write_artifacts(
        self,
        output_dir: str | PathLike[str] = DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR,
    ) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        config_path = target_dir / "counterfactual_config.json"
        scenario_path = target_dir / "scenario_definitions.csv"
        site_path = target_dir / "site_counterfactual_resolution.csv"
        reconstruction_summary_path = target_dir / "scenario_reconstruction_summary.csv"
        summary_vector_path = target_dir / "scenario_summary_vectors.csv"
        score_path = target_dir / "scenario_compatibility_scores.csv"
        ranking_path = target_dir / "scenario_rankings.csv"
        recommendation_path = target_dir / "recommendation.json"
        verification_path = target_dir / "verification.json"
        report_path = target_dir / "report.md"

        config_path.write_text(dumps(self.config_payload(), indent=2) + "\n", encoding="utf-8")
        write_rows(
            SCENARIO_DEFINITION_COLUMNS,
            (scenario.to_csv_row() for scenario in self.config.scenarios),
            scenario_path,
        )
        write_rows(
            SITE_COUNTERFACTUAL_COLUMNS, (row.to_csv_row() for row in self.site_rows), site_path
        )
        write_rows(
            SCENARIO_RECONSTRUCTION_SUMMARY_COLUMNS,
            (row.to_csv_row() for row in self.reconstruction_summary_rows),
            reconstruction_summary_path,
        )
        write_rows(
            SCENARIO_SUMMARY_VECTOR_COLUMNS,
            (row.to_csv_row() for row in self.summary_vector_rows),
            summary_vector_path,
        )
        write_rows(
            SCENARIO_COMPATIBILITY_SCORE_COLUMNS,
            (scenario_score_csv_row(row) for row in self.score_rows),
            score_path,
        )
        write_rows(
            SCENARIO_RANKING_COLUMNS,
            (scenario_ranking_csv_row(row) for row in self.ranking_rows),
            ranking_path,
        )
        recommendation_path.write_text(
            dumps(self.recommendation, indent=2) + "\n",
            encoding="utf-8",
        )
        verification_path.write_text(
            dumps(self.verification_payload(), indent=2) + "\n",
            encoding="utf-8",
        )
        report_path.write_text(
            render_observation_support_counterfactual_report(self),
            encoding="utf-8",
        )
        return (
            config_path,
            scenario_path,
            site_path,
            reconstruction_summary_path,
            summary_vector_path,
            score_path,
            ranking_path,
            recommendation_path,
            verification_path,
            report_path,
        )


def build_synth_small_observation_support_counterfactual_screen(
    *,
    evaluation_dir: str | PathLike[str] = DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    reconstruction_dir: str | PathLike[str] = DEFAULT_RECONSTRUCTION_DIR,
    observation_dir: str | PathLike[str] = DEFAULT_OBSERVATION_DIR,
    false_negative_audit_dir: str | PathLike[str] = DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
    summary_vector_dir: str | PathLike[str] = DEFAULT_SUMMARY_VECTOR_DIR,
    compatibility_screen_dir: str | PathLike[str] = DEFAULT_COMPATIBILITY_SCREEN_DIR,
    config: ObservationSupportCounterfactualConfig | None = None,
) -> SynthSmallObservationSupportCounterfactualResult:
    counterfactual_config = config or ObservationSupportCounterfactualConfig(
        evaluation_dir=str(evaluation_dir),
        reconstruction_dir=str(reconstruction_dir),
        observation_dir=str(observation_dir),
        false_negative_audit_dir=str(false_negative_audit_dir),
        summary_vector_dir=str(summary_vector_dir),
        compatibility_screen_dir=str(compatibility_screen_dir),
    )
    inputs = load_observation_support_counterfactual_inputs(
        evaluation_dir=counterfactual_config.evaluation_dir,
        reconstruction_dir=counterfactual_config.reconstruction_dir,
        observation_dir=counterfactual_config.observation_dir,
        false_negative_audit_dir=counterfactual_config.false_negative_audit_dir,
        summary_vector_dir=counterfactual_config.summary_vector_dir,
        compatibility_screen_dir=counterfactual_config.compatibility_screen_dir,
    )
    site_rows = build_site_counterfactual_rows(inputs, counterfactual_config)
    summary_targets = build_scenario_target_rows(inputs, site_rows, counterfactual_config)
    component_rows, coverage_rows, summary_vector_rows = build_scenario_summary_vector_rows(
        summary_targets,
        counterfactual_config,
    )
    score_rows, ranking_rows = build_scenario_compatibility_rows(
        component_rows=component_rows,
        coverage_rows=coverage_rows,
        config=counterfactual_config.compatibility_config,
    )
    reconstruction_summary_rows = build_scenario_reconstruction_summary_rows(
        component_rows=component_rows,
        site_rows=site_rows,
        ranking_rows=ranking_rows,
        inputs=inputs,
        scenarios=counterfactual_config.scenarios,
    )
    recommendation = build_counterfactual_recommendation(
        reconstruction_summary_rows=reconstruction_summary_rows,
        site_rows=site_rows,
    )
    checks = verify_observation_support_counterfactual_result(
        inputs=inputs,
        config=counterfactual_config,
        site_rows=site_rows,
        summary_vector_rows=summary_vector_rows,
        reconstruction_summary_rows=reconstruction_summary_rows,
        score_rows=score_rows,
        ranking_rows=ranking_rows,
        recommendation=recommendation,
    )
    return SynthSmallObservationSupportCounterfactualResult(
        config=counterfactual_config,
        inputs=inputs,
        site_rows=site_rows,
        summary_vector_rows=summary_vector_rows,
        reconstruction_summary_rows=reconstruction_summary_rows,
        score_rows=score_rows,
        ranking_rows=ranking_rows,
        recommendation=recommendation,
        verification_checks=checks,
    )


def load_observation_support_counterfactual_inputs(
    *,
    evaluation_dir: str | PathLike[str],
    reconstruction_dir: str | PathLike[str],
    observation_dir: str | PathLike[str],
    false_negative_audit_dir: str | PathLike[str],
    summary_vector_dir: str | PathLike[str],
    compatibility_screen_dir: str | PathLike[str],
) -> LoadedObservationSupportCounterfactualInputs:
    eval_dir = Path(evaluation_dir)
    recon_dir = Path(reconstruction_dir)
    obs_dir = Path(observation_dir)
    false_negative_dir = Path(false_negative_audit_dir)
    summary_dir = Path(summary_vector_dir)
    compatibility_dir = Path(compatibility_screen_dir)
    assert_required_files(eval_dir, EVALUATION_REQUIRED_FILES, "response-screen evaluation")
    assert_required_files(recon_dir, RECONSTRUCTION_REQUIRED_FILES, "reconstruction")
    assert_required_files(obs_dir, OBSERVATION_REQUIRED_FILES, "observations")
    assert_required_files(
        false_negative_dir,
        FALSE_NEGATIVE_AUDIT_REQUIRED_FILES,
        "false-negative audit",
    )
    assert_required_files(
        summary_dir, SUMMARY_VECTOR_BRIDGE_REQUIRED_FILES, "summary-vector bridge"
    )
    assert_required_files(
        compatibility_dir,
        COMPATIBILITY_BRIDGE_REQUIRED_FILES,
        "compatibility-screen bridge",
    )
    return LoadedObservationSupportCounterfactualInputs(
        evaluation_dir=eval_dir,
        reconstruction_dir=recon_dir,
        observation_dir=obs_dir,
        false_negative_audit_dir=false_negative_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        evaluation_summary=read_json(eval_dir / "screen_evaluation_summary.json"),
        site_evaluation_rows=read_csv_rows(eval_dir / "site_evaluation_audit.csv"),
        evaluation_verification=read_json(eval_dir / "verification.json"),
        reconstruction_config=read_json(recon_dir / "reconstruction_config.json"),
        reconstruction_rows=read_csv_rows(recon_dir / "site_reconstruction.csv"),
        reconstruction_verification=read_json(recon_dir / "verification.json"),
        truth_rows=read_csv_rows(obs_dir / "evaluation_truth.csv"),
        truth_reference=read_json(obs_dir / "truth_reference.json"),
        false_negative_config=read_json(false_negative_dir / "false_negative_audit_config.json"),
        false_negative_site_rows=read_csv_rows(
            false_negative_dir / "false_negative_site_audit.csv"
        ),
        false_negative_mechanism_rows=read_csv_rows(false_negative_dir / "mechanism_summary.csv"),
        false_negative_recommendation=read_json(false_negative_dir / "recommendation.json"),
        false_negative_verification=read_json(false_negative_dir / "verification.json"),
        summary_vector_mode_summary=read_json(summary_dir / "mode_summary.json"),
        summary_vector_verification=read_json(summary_dir / "verification.json"),
        compatibility_target_summary=read_json(compatibility_dir / "target_summary.json"),
        compatibility_candidate_score_rows=read_csv_rows(
            compatibility_dir / "candidate_scores.csv"
        ),
        compatibility_mode_ranking_rows=read_csv_rows(compatibility_dir / "mode_rankings.csv"),
        compatibility_verification=read_json(compatibility_dir / "verification.json"),
    )


def build_site_counterfactual_rows(
    inputs: LoadedObservationSupportCounterfactualInputs,
    config: ObservationSupportCounterfactualConfig,
) -> tuple[SiteCounterfactualResolutionRow, ...]:
    output: list[SiteCounterfactualResolutionRow] = []
    min_run = min_final_absence_run(inputs.reconstruction_config)
    for scenario in config.scenarios:
        for row in inputs.false_negative_site_rows:
            output.append(
                build_site_counterfactual_row(
                    scenario=scenario,
                    row=row,
                    min_final_absence_run_value=min_run,
                    support_delay=config.support_delay,
                    support_interval=config.support_interval,
                )
            )
    return tuple(output)


def build_site_counterfactual_row(
    *,
    scenario: CounterfactualScenario,
    row: dict[str, str],
    min_final_absence_run_value: int,
    support_delay: float,
    support_interval: float,
) -> SiteCounterfactualResolutionRow:
    true_extirpation = parse_required_float(row["true_extirpation_time"])
    post_detection_count = parse_int(row["post_extirpation_detection_count"])
    status_quo_time = parse_optional_float(row["observed_extirpation_time"])
    unresolved_reason = ""
    resolved = False
    support_start: float | None = None
    support_count = 0
    resolution_rule = "status_quo_no_support"

    if not scenario.applies_support:
        unresolved_reason = "status_quo_no_counterfactual_support"
    elif scenario.respects_post_extirpation_detections and post_detection_count > 0:
        unresolved_reason = "post_extirpation_detection_blocker"
    elif scenario.timing_gap_only and row["primary_mechanism"] not in TIMING_GAP_MECHANISMS:
        unresolved_reason = "not_timing_gap_false_negative"
    else:
        resolved = True
        support_start = true_extirpation + support_delay
        if scenario.late_followup:
            last_survey_time = parse_optional_float(row["last_survey_time"])
            if last_survey_time is not None:
                support_start = max(support_start, last_survey_time + support_interval)
        support_count = min_final_absence_run_value
        resolution_rule = scenario.scenario_id

    return SiteCounterfactualResolutionRow(
        scenario_id=scenario.scenario_id,
        site_id=row["site_id"],
        cell_id=parse_int(row["cell_id"]),
        row=parse_int(row["row"]),
        col=parse_int(row["col"]),
        region=row["region"],
        front_band=row["front_band"],
        primary_mechanism=row["primary_mechanism"],
        post_extirpation_detection_count=post_detection_count,
        status_quo_observed_extirpation_time=status_quo_time,
        true_extirpation_time=true_extirpation,
        counterfactual_observed_extirpation_time=support_start if resolved else None,
        resolved_false_negative=resolved,
        resolution_rule=resolution_rule,
        unresolved_reason="" if resolved else unresolved_reason,
        synthetic_support_start_time=support_start,
        synthetic_support_survey_count=support_count,
    )


def build_scenario_target_rows(
    inputs: LoadedObservationSupportCounterfactualInputs,
    site_rows: tuple[SiteCounterfactualResolutionRow, ...],
    config: ObservationSupportCounterfactualConfig,
) -> dict[str, tuple[SummaryVectorTargetRow, ...]]:
    reconstruction_by_site = {row["site_id"]: row for row in inputs.reconstruction_rows}
    resolved_by_scenario_site = {
        (row.scenario_id, row.site_id): row for row in site_rows if row.resolved_false_negative
    }
    output: dict[str, tuple[SummaryVectorTargetRow, ...]] = {}
    for scenario in config.scenarios:
        target_rows: list[SummaryVectorTargetRow] = []
        for truth_row in inputs.truth_rows:
            site_id = truth_row["site_id"]
            reconstruction_row = reconstruction_by_site[site_id]
            target_time = parse_optional_float(reconstruction_row["observed_extirpation_time"])
            resolution = resolved_by_scenario_site.get((scenario.scenario_id, site_id))
            if resolution is not None:
                target_time = resolution.counterfactual_observed_extirpation_time
            target_rows.append(
                SummaryVectorTargetRow(
                    site_id=site_id,
                    cell_id=parse_int(truth_row["cell_id"]),
                    grid_row=parse_int(truth_row["row"]),
                    grid_col=parse_int(truth_row["col"]),
                    driver_arrival=parse_optional_float(truth_row["driver_arrival"]),
                    target_time=target_time,
                )
            )
        output[scenario.scenario_id] = tuple(target_rows)
    return output


def build_scenario_summary_vector_rows(
    target_rows_by_scenario: dict[str, tuple[SummaryVectorTargetRow, ...]],
    config: ObservationSupportCounterfactualConfig,
) -> tuple[
    dict[str, tuple[SummaryComponentRow, ...]],
    dict[str, tuple[CoverageCurveRow, ...]],
    tuple[ScenarioSummaryVectorRow, ...],
]:
    component_rows_by_scenario: dict[str, tuple[SummaryComponentRow, ...]] = {}
    coverage_rows_by_scenario: dict[str, tuple[CoverageCurveRow, ...]] = {}
    summary_rows: list[ScenarioSummaryVectorRow] = []
    for scenario in config.scenarios:
        scenario_id = scenario.scenario_id
        component_rows = build_summary_component_rows(
            scenario_id,
            target_rows_by_scenario[scenario_id],
        )
        coverage_rows = build_coverage_curve_rows(
            mode=scenario_id,
            rows=target_rows_by_scenario[scenario_id],
            coverage_breakpoints=config.coverage_breakpoints,
        )
        component_rows_by_scenario[scenario_id] = component_rows
        coverage_rows_by_scenario[scenario_id] = coverage_rows
        summary_rows.extend(
            ScenarioSummaryVectorRow(
                scenario_id=scenario_id,
                row_type="summary_component",
                metric=row.component,
                value=row.value,
                missing_reason=row.missing_reason,
            )
            for row in component_rows
        )
        summary_rows.extend(
            ScenarioSummaryVectorRow(
                scenario_id=scenario_id,
                row_type="coverage_curve",
                metric="target_time",
                value=row.target_time,
                coverage_fraction=row.coverage_fraction,
                finite_target_count=row.finite_target_count,
                missing_reason=row.missing_reason,
            )
            for row in coverage_rows
        )
    return component_rows_by_scenario, coverage_rows_by_scenario, tuple(summary_rows)


def build_scenario_compatibility_rows(
    *,
    component_rows: dict[str, tuple[SummaryComponentRow, ...]],
    coverage_rows: dict[str, tuple[CoverageCurveRow, ...]],
    config: CompatibilityScreenConfig,
) -> tuple[tuple[CandidateScoreRow, ...], tuple[ModeRankingRow, ...]]:
    scenario_ids = tuple(component_rows)
    screen_config = CompatibilityScreenConfig(
        target_modes=scenario_ids,
        primary_target_mode="status_quo",
        candidates=config.candidates,
        coverage_breakpoints=config.coverage_breakpoints,
        required_components=config.required_components,
        gap_settings=config.gap_settings,
        compatible_loss_max=config.compatible_loss_max,
        borderline_loss_max=config.borderline_loss_max,
    )
    profiles = tuple(
        build_candidate_profile(
            candidate,
            coverage_breakpoints=screen_config.coverage_breakpoints,
        )
        for candidate in screen_config.candidates
    )
    settings_by_component = {setting.component: setting for setting in screen_config.gap_settings}
    mode_scores = []
    score_rows: list[CandidateScoreRow] = []
    for scenario_id in scenario_ids:
        target_components = {
            row.component: scalar_value(row.value, row.missing_reason)
            for row in component_rows[scenario_id]
        }
        target_coverage = {
            row.coverage_fraction: scalar_value(row.target_time, row.missing_reason)
            for row in coverage_rows[scenario_id]
        }
        for profile in profiles:
            mode_score, rows, _coverage_score_rows = score_candidate_against_target(
                target_mode=scenario_id,
                target_components=target_components,
                target_coverage=target_coverage,
                profile=profile,
                config=screen_config,
                settings_by_component=settings_by_component,
            )
            mode_scores.append(mode_score)
            score_rows.extend(rows)
    return tuple(score_rows), build_mode_rankings(mode_scores, config=screen_config)


def build_scenario_reconstruction_summary_rows(
    *,
    component_rows: dict[str, tuple[SummaryComponentRow, ...]],
    site_rows: tuple[SiteCounterfactualResolutionRow, ...],
    ranking_rows: tuple[ModeRankingRow, ...],
    inputs: LoadedObservationSupportCounterfactualInputs,
    scenarios: tuple[CounterfactualScenario, ...],
) -> tuple[ScenarioReconstructionSummaryRow, ...]:
    false_negative_count = expected_false_negative_count(inputs)
    ideal_true_count = ideal_true_finite_target_count(inputs)
    finite_by_scenario = {
        scenario_id: finite_target_count(rows) for scenario_id, rows in component_rows.items()
    }
    fraction_by_scenario = {
        scenario_id: finite_target_fraction(rows) for scenario_id, rows in component_rows.items()
    }
    status_quo_finite = finite_by_scenario["status_quo"]
    first_rank_by_scenario = {row.target_mode: row for row in ranking_rows if row.rank == 1}
    output: list[ScenarioReconstructionSummaryRow] = []
    for scenario in scenarios:
        rows = [row for row in site_rows if row.scenario_id == scenario.scenario_id]
        resolved_count = sum(row.resolved_false_negative for row in rows)
        post_detection_blocker_count = sum(row.post_extirpation_detection_count > 0 for row in rows)
        remaining_post_detection_blocker_count = sum(
            row.post_extirpation_detection_count > 0 and not row.resolved_false_negative
            for row in rows
        )
        top_rank = first_rank_by_scenario[scenario.scenario_id]
        output.append(
            ScenarioReconstructionSummaryRow(
                scenario_id=scenario.scenario_id,
                finite_target_count=finite_by_scenario[scenario.scenario_id],
                finite_target_fraction=fraction_by_scenario[scenario.scenario_id],
                ideal_true_finite_target_count=ideal_true_count,
                status_quo_finite_target_count=status_quo_finite,
                false_negative_count=false_negative_count,
                resolved_false_negative_count=resolved_count,
                remaining_false_negative_count=false_negative_count - resolved_count,
                post_extirpation_detection_blocker_count=post_detection_blocker_count,
                remaining_post_extirpation_detection_blocker_count=(
                    remaining_post_detection_blocker_count
                ),
                top_candidate_label=top_rank.candidate.label,
                top_total_weighted_loss=top_rank.total_weighted_loss,
                top_compatibility_class=top_rank.compatibility_class,
                restores_status_quo_finite_drop=(
                    finite_by_scenario[scenario.scenario_id] >= ideal_true_count
                    and status_quo_finite < ideal_true_count
                ),
                restores_compatibility=top_rank.compatibility_class == "compatible",
            )
        )
    return tuple(output)


def build_counterfactual_recommendation(
    *,
    reconstruction_summary_rows: tuple[ScenarioReconstructionSummaryRow, ...],
    site_rows: tuple[SiteCounterfactualResolutionRow, ...],
) -> dict[str, Any]:
    rows_by_scenario = summary_by_scenario(reconstruction_summary_rows)
    compatible = [row for row in reconstruction_summary_rows if row.restores_compatibility]
    finite_restored = [
        row for row in reconstruction_summary_rows if row.restores_status_quo_finite_drop
    ]
    blocker_counts = Counter(
        row.primary_mechanism
        for row in site_rows
        if row.scenario_id == "detection_blocker_respecting_floor"
        and not row.resolved_false_negative
    )
    if compatible:
        recommendation_class = "counterfactual_support_restores_compatibility"
    elif finite_restored:
        recommendation_class = "finite_target_support_improves_but_compatibility_not_restored"
    else:
        recommendation_class = "observation_support_insufficient_under_current_bridge"
    return {
        **counterfactual_labels(),
        "recommendation_class": recommendation_class,
        "status_quo": summary_row_payload(rows_by_scenario["status_quo"]),
        "best_finite_target_scenario": summary_row_payload(
            max(reconstruction_summary_rows, key=lambda row: row.finite_target_count)
        ),
        "best_loss_scenario": summary_row_payload(
            min(
                reconstruction_summary_rows,
                key=lambda row: (
                    row.top_total_weighted_loss
                    if row.top_total_weighted_loss is not None
                    else float("inf")
                ),
            )
        ),
        "compatibility_restored_by": [row.scenario_id for row in compatible],
        "finite_target_count_restored_by": [row.scenario_id for row in finite_restored],
        "remaining_blocker_classes": dict(sorted(blocker_counts.items())),
        "interpretation": (
            "Counterfactual support improves finite target support, but unchanged "
            "Goal 010 compatibility thresholds and candidates still govern the result."
        ),
    }


def verify_observation_support_counterfactual_result(
    *,
    inputs: LoadedObservationSupportCounterfactualInputs,
    config: ObservationSupportCounterfactualConfig,
    site_rows: tuple[SiteCounterfactualResolutionRow, ...],
    summary_vector_rows: tuple[ScenarioSummaryVectorRow, ...],
    reconstruction_summary_rows: tuple[ScenarioReconstructionSummaryRow, ...],
    score_rows: tuple[CandidateScoreRow, ...],
    ranking_rows: tuple[ModeRankingRow, ...],
    recommendation: dict[str, Any],
) -> tuple[ObservationSupportCounterfactualCheck, ...]:
    source_passed = source_verifications(inputs)
    expected_fn_count = expected_false_negative_count(inputs)
    scenario_ids = tuple(scenario.scenario_id for scenario in config.scenarios)
    summary_rows = summary_by_scenario(reconstruction_summary_rows)
    row_counts_by_scenario = Counter(row.scenario_id for row in site_rows)
    score_counts_by_scenario = Counter(row.target_mode for row in score_rows)
    ranking_counts_by_scenario = Counter(row.target_mode for row in ranking_rows)
    status_quo = summary_rows.get("status_quo")
    all_support = summary_rows.get("truth_guided_absence_floor_all")
    bridge_reconciliation = bridge_reconciliation_payload(
        inputs=inputs,
        reconstruction_summary_rows=reconstruction_summary_rows,
    )
    expected_score_rows = (
        len(scenario_ids)
        * len(config.compatibility_config.candidates)
        * (len(config.compatibility_config.required_components) + 1)
    )
    return (
        ObservationSupportCounterfactualCheck(
            name="source_verifications",
            passed=all(source_passed.values()),
            message="all prerequisite verification payloads passed",
            details=source_passed,
        ),
        ObservationSupportCounterfactualCheck(
            name="scenario_set",
            passed=scenario_ids == SCENARIO_IDS,
            message="scenario set is small, deterministic, and ordered",
            details={"scenario_ids": list(scenario_ids)},
        ),
        ObservationSupportCounterfactualCheck(
            name="site_resolution_rows",
            passed=all(
                row_counts_by_scenario[scenario_id] == expected_fn_count
                for scenario_id in scenario_ids
            ),
            message="each scenario has one site-resolution row per false negative",
            details={
                "expected_false_negative_count": expected_fn_count,
                "row_counts_by_scenario": dict(row_counts_by_scenario),
            },
        ),
        ObservationSupportCounterfactualCheck(
            name="status_quo_reconciliation",
            passed=status_quo is not None
            and status_quo.finite_target_count == 151
            and status_quo.false_negative_count == expected_fn_count == 101
            and status_quo.top_compatibility_class == "incompatible",
            message="status quo reconciles Goal 010-012 finite-target and false-negative counts",
            details={}
            if status_quo is None
            else {
                "finite_target_count": status_quo.finite_target_count,
                "false_negative_count": status_quo.false_negative_count,
                "top_compatibility_class": status_quo.top_compatibility_class,
            },
        ),
        ObservationSupportCounterfactualCheck(
            name="bridge_artifact_reconciliation",
            passed=bool(bridge_reconciliation["status_quo_matches_existing_goal010"])
            and bool(bridge_reconciliation["ideal_true_finite_target_count_matches"])
            and bool(bridge_reconciliation["goal010_default_score_sum_matches_ranking_loss"]),
            message=("status quo reconciles against existing Goal 009/010 bridge artifacts"),
            details=bridge_reconciliation,
        ),
        ObservationSupportCounterfactualCheck(
            name="finite_target_restoration",
            passed=all_support is not None
            and all_support.finite_target_count == all_support.ideal_true_finite_target_count,
            message="upper-bound support scenario restores the finite-target count",
            details={}
            if all_support is None
            else {
                "finite_target_count": all_support.finite_target_count,
                "ideal_true_finite_target_count": all_support.ideal_true_finite_target_count,
            },
        ),
        ObservationSupportCounterfactualCheck(
            name="summary_vectors",
            passed={row.scenario_id for row in summary_vector_rows} == set(scenario_ids)
            and {row.row_type for row in summary_vector_rows}
            == {"summary_component", "coverage_curve"},
            message="scenario summary vectors contain scalar and coverage rows",
            details={"summary_vector_row_count": len(summary_vector_rows)},
        ),
        ObservationSupportCounterfactualCheck(
            name="compatibility_rows",
            passed=len(score_rows) == expected_score_rows
            and all(
                ranking_counts_by_scenario[scenario_id]
                == len(config.compatibility_config.candidates)
                for scenario_id in scenario_ids
            )
            and all(score_counts_by_scenario[scenario_id] > 0 for scenario_id in scenario_ids),
            message="compatibility scores and rankings were emitted for every scenario",
            details={
                "score_row_count": len(score_rows),
                "expected_score_row_count": expected_score_rows,
                "ranking_counts_by_scenario": dict(ranking_counts_by_scenario),
            },
        ),
        ObservationSupportCounterfactualCheck(
            name="recommendation",
            passed=recommendation["recommendation_class"]
            == "finite_target_support_improves_but_compatibility_not_restored",
            message="recommendation remains diagnostic before rule/design/inference changes",
            details={"recommendation_class": recommendation["recommendation_class"]},
        ),
    )


def render_observation_support_counterfactual_report(
    result: SynthSmallObservationSupportCounterfactualResult,
) -> str:
    lines = [
        "# Synth-Small Observation-Support Counterfactual Screen",
        "",
        "## Scope",
        "",
        (
            "This is a synthetic-only, evaluation-only, counterfactual-only screen. "
            "It does not change default observation design, production "
            "reconstruction rules, scoring, candidates, or inference logic."
        ),
        "",
        "## Scenario Summary",
        "",
        "| Scenario | Finite targets | Resolved false negatives | Top candidate | Loss | Class |",
        "| --- | ---: | ---: | --- | ---: | --- |",
    ]
    for row in result.reconstruction_summary_rows:
        lines.append(
            "| "
            f"`{row.scenario_id}` | `{row.finite_target_count}` | "
            f"`{row.resolved_false_negative_count}` | `{row.top_candidate_label}` | "
            f"`{stringify_optional_float(row.top_total_weighted_loss)}` | "
            f"`{row.top_compatibility_class}` |"
        )
    recommendation = result.recommendation
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"- Class: `{recommendation['recommendation_class']}`",
            "- Compatibility restored by: "
            f"`{', '.join(recommendation['compatibility_restored_by']) or 'none'}`",
            "- Finite-target count restored by: "
            f"`{', '.join(recommendation['finite_target_count_restored_by']) or 'none'}`",
            "",
            "## Interpretation Limit",
            "",
            (
                "The truth-guided support scenarios are diagnostic upper bounds or "
                "bounded counterfactuals. They are not analyst-facing survey designs, "
                "and any reconstruction, observation, candidate, ABC, or POM change "
                "requires a later bounded goal."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def counterfactual_labels() -> dict[str, bool]:
    return {key: True for key in COUNTERFACTUAL_LABEL_KEYS}


def source_verifications(inputs: LoadedObservationSupportCounterfactualInputs) -> dict[str, bool]:
    return {
        "response_screen_evaluation": bool(inputs.evaluation_verification.get("passed")),
        "extirpation_reconstruction": bool(inputs.reconstruction_verification.get("passed")),
        "false_negative_audit": bool(inputs.false_negative_verification.get("passed")),
        "summary_vector": bool(inputs.summary_vector_verification.get("passed")),
        "compatibility_screen": bool(inputs.compatibility_verification.get("passed")),
        "observation_inputs_present": bool(inputs.truth_reference),
    }


def bridge_reconciliation_payload(
    *,
    inputs: LoadedObservationSupportCounterfactualInputs,
    reconstruction_summary_rows: tuple[ScenarioReconstructionSummaryRow, ...],
) -> dict[str, Any]:
    summaries = summary_by_scenario(reconstruction_summary_rows)
    status_quo = summaries["status_quo"]
    summary_vector_modes = dict_payload(inputs.summary_vector_mode_summary.get("mode_summaries"))
    target_summary_modes = dict_payload(inputs.compatibility_target_summary.get("mode_summaries"))
    summary_vector_realistic = dict_payload(summary_vector_modes.get("realistic_observed"))
    summary_vector_ideal = dict_payload(summary_vector_modes.get("ideal_true"))
    target_summary_realistic = dict_payload(target_summary_modes.get("realistic_observed"))
    target_summary_ideal = dict_payload(target_summary_modes.get("ideal_true"))
    goal010_top = goal010_realistic_observed_top_row(inputs)
    goal010_top_loss = parse_optional_float(goal010_top.get("total_weighted_loss", ""))
    goal010_default_score_sum = goal010_realistic_observed_default_score_sum(inputs)
    status_quo_matches_existing_goal010 = (
        int_payload(summary_vector_realistic.get("finite_target_count"), -1)
        == status_quo.finite_target_count
        and int_payload(target_summary_realistic.get("finite_target_count"), -1)
        == status_quo.finite_target_count
        and goal010_top.get("candidate_label") == status_quo.top_candidate_label
        and goal010_top.get("compatibility_class") == status_quo.top_compatibility_class
        and approx_equal(goal010_top_loss, status_quo.top_total_weighted_loss)
    )
    ideal_count = status_quo.ideal_true_finite_target_count
    ideal_true_matches = (
        int_payload(summary_vector_ideal.get("finite_target_count"), -1) == ideal_count
        and int_payload(target_summary_ideal.get("finite_target_count"), -1) == ideal_count
    )
    score_sum_matches = approx_equal(goal010_default_score_sum, goal010_top_loss)
    return {
        "summary_vector_realistic_observed_finite_target_count": int_payload(
            summary_vector_realistic.get("finite_target_count"), -1
        ),
        "summary_vector_ideal_true_finite_target_count": int_payload(
            summary_vector_ideal.get("finite_target_count"), -1
        ),
        "compatibility_target_realistic_observed_finite_target_count": int_payload(
            target_summary_realistic.get("finite_target_count"), -1
        ),
        "compatibility_target_ideal_true_finite_target_count": int_payload(
            target_summary_ideal.get("finite_target_count"), -1
        ),
        "goal010_realistic_observed_top_candidate_label": goal010_top.get("candidate_label", ""),
        "goal010_realistic_observed_top_compatibility_class": goal010_top.get(
            "compatibility_class", ""
        ),
        "goal010_realistic_observed_top_total_weighted_loss": goal010_top_loss,
        "goal010_realistic_observed_default_score_sum": goal010_default_score_sum,
        "status_quo_finite_target_count": status_quo.finite_target_count,
        "status_quo_top_candidate_label": status_quo.top_candidate_label,
        "status_quo_top_compatibility_class": status_quo.top_compatibility_class,
        "status_quo_top_total_weighted_loss": status_quo.top_total_weighted_loss,
        "status_quo_matches_existing_goal010": status_quo_matches_existing_goal010,
        "ideal_true_finite_target_count_matches": ideal_true_matches,
        "goal010_default_score_sum_matches_ranking_loss": score_sum_matches,
    }


def goal010_realistic_observed_top_row(
    inputs: LoadedObservationSupportCounterfactualInputs,
) -> dict[str, str]:
    rows = [
        row
        for row in inputs.compatibility_mode_ranking_rows
        if row["target_mode"] == "realistic_observed" and row["rank"] == "1"
    ]
    return rows[0] if rows else {}


def goal010_realistic_observed_default_score_sum(
    inputs: LoadedObservationSupportCounterfactualInputs,
) -> float | None:
    score_values = [
        parse_optional_float(row["weighted_gap"])
        for row in inputs.compatibility_candidate_score_rows
        if row["target_mode"] == "realistic_observed" and row["candidate_label"] == "default"
    ]
    finite_values = [value for value in score_values if value is not None]
    if not finite_values:
        return None
    return sum(finite_values)


def approx_equal(left: float | None, right: float | None, *, tolerance: float = 1e-9) -> bool:
    if left is None or right is None:
        return False
    return abs(left - right) <= tolerance


def summary_by_scenario(
    rows: tuple[ScenarioReconstructionSummaryRow, ...],
) -> dict[str, ScenarioReconstructionSummaryRow]:
    return {row.scenario_id: row for row in rows}


def summary_row_payload(row: ScenarioReconstructionSummaryRow) -> dict[str, Any]:
    return {
        "scenario_id": row.scenario_id,
        "finite_target_count": row.finite_target_count,
        "resolved_false_negative_count": row.resolved_false_negative_count,
        "remaining_false_negative_count": row.remaining_false_negative_count,
        "top_candidate_label": row.top_candidate_label,
        "top_total_weighted_loss": row.top_total_weighted_loss,
        "top_compatibility_class": row.top_compatibility_class,
        "restores_status_quo_finite_drop": row.restores_status_quo_finite_drop,
        "restores_compatibility": row.restores_compatibility,
    }


def min_final_absence_run(reconstruction_config: dict[str, Any]) -> int:
    config = dict_payload(reconstruction_config.get("config"))
    return int_payload(config.get("min_final_absence_run"), 2)


def expected_false_negative_count(inputs: LoadedObservationSupportCounterfactualInputs) -> int:
    classification = dict_payload(inputs.evaluation_summary.get("classification"))
    if "false_negative_count" in classification:
        return int_payload(classification["false_negative_count"], 0)
    matrix = dict_payload(classification.get("confusion_matrix"))
    return int_payload(matrix.get("fn"), 0)


def ideal_true_finite_target_count(inputs: LoadedObservationSupportCounterfactualInputs) -> int:
    return sum(
        parse_optional_float(row["true_extirpation"]) is not None for row in inputs.truth_rows
    )


def finite_target_count(rows: tuple[SummaryComponentRow, ...]) -> int:
    row = next(component for component in rows if component.component == "finite_target_count")
    return int(float(row.value))


def finite_target_fraction(rows: tuple[SummaryComponentRow, ...]) -> float:
    row = next(component for component in rows if component.component == "finite_target_fraction")
    return parse_required_float(row.value)


def scenario_score_csv_row(row: CandidateScoreRow) -> tuple[str, ...]:
    return row.to_csv_row()


def scenario_ranking_csv_row(row: ModeRankingRow) -> tuple[str, ...]:
    return row.to_csv_row()


def assert_required_files(path: Path, names: tuple[str, ...], label: str) -> None:
    missing = [name for name in names if not (path / name).exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(f"missing required {label} artifacts: {missing_text}")


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return dict_payload(loads(path.read_text(encoding="utf-8")))


def write_rows(columns: tuple[str, ...], rows: Iterable[tuple[str, ...]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(columns)
        csv_writer.writerows(rows)


def parse_int(value: str) -> int:
    return int(value)


def parse_required_float(value: str) -> float:
    if value == "":
        raise ValueError("expected finite float, got blank value")
    parsed = float(value)
    if not isfinite(parsed):
        raise ValueError(f"expected finite float, got {value!r}")
    return parsed


def parse_optional_float(value: str) -> float | None:
    if value == "":
        return None
    parsed = float(value)
    if not isfinite(parsed):
        return None
    return parsed


def stringify_optional_float(value: float | None) -> str:
    if value is None:
        return ""
    return stringify_float(value)


def stringify_bool(value: bool) -> str:
    return str(value).lower()


def dict_payload(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def int_payload(value: Any, fallback: int) -> int:
    if isinstance(value, bool):
        return fallback
    if isinstance(value, int):
        return value
    if isinstance(value, float) and isfinite(value):
        return int(value)
    return fallback


__all__ = [
    "DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR",
    "OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_FILES",
    "ObservationSupportCounterfactualCheck",
    "ObservationSupportCounterfactualConfig",
    "ScenarioReconstructionSummaryRow",
    "ScenarioSummaryVectorRow",
    "SiteCounterfactualResolutionRow",
    "SynthSmallObservationSupportCounterfactualResult",
    "build_synth_small_observation_support_counterfactual_screen",
    "default_counterfactual_scenarios",
    "render_observation_support_counterfactual_report",
]
