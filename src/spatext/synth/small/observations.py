from __future__ import annotations

from csv import DictReader, writer
from dataclasses import asdict, dataclass, field
from json import dumps, loads
from os import PathLike
from pathlib import Path
from typing import Any, cast

import numpy as np

from .predator import SynthSmallPredatorTruthResult, build_synth_small_predator_truth

DEFAULT_OUTPUT_DIR = Path("artifacts/synth_small_observations")

ANALYST_FACING_FILES = ("sites.csv", "visits.csv", "observations.csv")
FORBIDDEN_ANALYST_COLUMNS = frozenset(
    {
        "driver_arrival",
        "predator_pressure",
        "true_extirpation",
        "extirpation_lag",
        "extirpated_by_end",
        "initial_abundance",
        "final_abundance",
    }
)
REQUIRED_OBSERVATION_FILES = (
    "observation_config.json",
    "truth_reference.json",
    "sites.csv",
    "visits.csv",
    "observations.csv",
    "evaluation_truth.csv",
)
SITE_COLUMNS = ("site_id", "cell_id", "row", "col", "region", "front_band")
VISIT_COLUMNS = (
    "visit_id",
    "site_id",
    "cell_id",
    "time_index",
    "visit_replicate",
    "effort",
    "region",
)
OBSERVATION_COLUMNS = (
    "visit_id",
    "site_id",
    "cell_id",
    "time_index",
    "visit_replicate",
    "effort",
    "observed_count",
    "detected",
)
EVALUATION_TRUTH_COLUMNS = (
    "site_id",
    "cell_id",
    "row",
    "col",
    "driver_arrival",
    "true_extirpation",
    "extirpation_lag",
    "extirpated_by_end",
    "initial_abundance",
    "final_abundance",
)


@dataclass(frozen=True, slots=True)
class ObservationSurveyConfig:
    seed: int = 20260530
    survey_interval: int = 4
    replicate_visits: int = 2
    base_visit_probability: float = 0.58
    west_visit_bonus: float = 0.12
    central_visit_bonus: float = 0.06
    east_visit_bonus: float = -0.05
    suitability_visit_weight: float = 0.16
    base_effort: float = 1.0
    effort_noise_sigma: float = 0.15


@dataclass(frozen=True, slots=True)
class ObservationDetectionConfig:
    count_scale: float = 2.5
    detection_half_saturation: float = 8.0


@dataclass(frozen=True, slots=True)
class SynthSmallObservationConfig:
    survey: ObservationSurveyConfig = field(default_factory=ObservationSurveyConfig)
    detection: ObservationDetectionConfig = field(default_factory=ObservationDetectionConfig)
    truth_artifact_dir: str = "artifacts/synth_small_predator_truth"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SiteRow:
    site_id: str
    cell_id: int
    row: int
    col: int
    region: str
    front_band: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.site_id,
            str(self.cell_id),
            str(self.row),
            str(self.col),
            self.region,
            self.front_band,
        )


@dataclass(frozen=True, slots=True)
class VisitRow:
    visit_id: str
    site_id: str
    cell_id: int
    time_index: int
    visit_replicate: int
    effort: float
    region: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.visit_id,
            self.site_id,
            str(self.cell_id),
            str(self.time_index),
            str(self.visit_replicate),
            stringify_float(self.effort),
            self.region,
        )


@dataclass(frozen=True, slots=True)
class ObservationRow:
    visit_id: str
    site_id: str
    cell_id: int
    time_index: int
    visit_replicate: int
    effort: float
    observed_count: int
    detected: bool

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.visit_id,
            self.site_id,
            str(self.cell_id),
            str(self.time_index),
            str(self.visit_replicate),
            stringify_float(self.effort),
            str(self.observed_count),
            stringify_bool(self.detected),
        )


@dataclass(frozen=True, slots=True)
class EvaluationTruthRow:
    site_id: str
    cell_id: int
    row: int
    col: int
    driver_arrival: int
    true_extirpation: float | None
    extirpation_lag: float | None
    extirpated_by_end: bool
    initial_abundance: float
    final_abundance: float

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.site_id,
            str(self.cell_id),
            str(self.row),
            str(self.col),
            str(self.driver_arrival),
            stringify_nullable_float(self.true_extirpation),
            stringify_nullable_float(self.extirpation_lag),
            stringify_bool(self.extirpated_by_end),
            stringify_float(self.initial_abundance),
            stringify_float(self.final_abundance),
        )


@dataclass(frozen=True, slots=True)
class ObservationDiagnostics:
    simulation_horizon: int
    survey_times: tuple[int, ...]
    scheduled_site_time_count: int
    visited_site_time_count: int
    total_visits: int
    unique_sites_visited: int
    observation_count: int
    detection_count: int
    mean_effort: float
    mean_observed_count: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "simulation_horizon": self.simulation_horizon,
            "survey_times": list(self.survey_times),
            "scheduled_site_time_count": self.scheduled_site_time_count,
            "visited_site_time_count": self.visited_site_time_count,
            "total_visits": self.total_visits,
            "unique_sites_visited": self.unique_sites_visited,
            "observation_count": self.observation_count,
            "detection_count": self.detection_count,
            "mean_effort": self.mean_effort,
            "mean_observed_count": self.mean_observed_count,
        }


@dataclass(frozen=True, slots=True)
class SynthSmallObservationResult:
    config: SynthSmallObservationConfig
    truth: SynthSmallPredatorTruthResult
    site_rows: tuple[SiteRow, ...]
    visit_rows: tuple[VisitRow, ...]
    observation_rows: tuple[ObservationRow, ...]
    evaluation_truth_rows: tuple[EvaluationTruthRow, ...]
    diagnostics: ObservationDiagnostics

    def write_artifacts(self, output_dir: str | PathLike[str]) -> tuple[Path, ...]:
        return write_synth_small_observation_artifacts(self, output_dir)


@dataclass(frozen=True, slots=True)
class LoadedSynthSmallObservationBundle:
    artifact_dir: Path
    observation_config: dict[str, Any]
    truth_reference: dict[str, Any]
    sites: tuple[dict[str, str], ...]
    visits: tuple[dict[str, str], ...]
    observations: tuple[dict[str, str], ...]
    evaluation_truth: tuple[dict[str, str], ...]


@dataclass(frozen=True, slots=True)
class ObservationVerificationCheck:
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
class ObservationSummaryRow:
    section: str
    metric: str
    value: str

    def to_csv_row(self) -> tuple[str, str, str]:
        return (self.section, self.metric, self.value)


@dataclass(frozen=True, slots=True)
class SynthSmallObservationInspectionResult:
    artifact_dir: Path
    output_dir: Path
    verification_checks: tuple[ObservationVerificationCheck, ...]
    observation_summary_rows: tuple[ObservationSummaryRow, ...]
    recoverability_smoke: dict[str, Any]
    verification_path: Path
    observation_summary_path: Path
    recoverability_smoke_path: Path
    report_path: Path

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def verification_payload(self) -> dict[str, Any]:
        return {
            "artifact_dir": str(self.artifact_dir),
            "output_dir": str(self.output_dir),
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.verification_checks],
        }


def default_synth_small_observation_config() -> SynthSmallObservationConfig:
    return SynthSmallObservationConfig()


def build_synth_small_observations(
    config: SynthSmallObservationConfig | None = None,
    *,
    truth: SynthSmallPredatorTruthResult | None = None,
) -> SynthSmallObservationResult:
    observation_config = config or default_synth_small_observation_config()
    validate_observation_config(observation_config)
    truth_result = truth or build_synth_small_predator_truth()
    rng = np.random.default_rng(observation_config.survey.seed)
    survey_times = build_survey_times(
        truth_result.diagnostics.simulation_horizon,
        observation_config.survey.survey_interval,
    )
    site_rows = build_site_rows(truth_result)
    evaluation_truth_rows = build_evaluation_truth_rows(truth_result, site_rows)
    visit_rows: list[VisitRow] = []
    observation_rows: list[ObservationRow] = []
    visited_site_times: set[tuple[str, int]] = set()

    suitability_min = float(np.min(truth_result.suitability))
    suitability_max = float(np.max(truth_result.suitability))
    suitability_range = max(suitability_max - suitability_min, 1e-12)
    visit_id_index = 0
    for site in site_rows:
        suitability = float(truth_result.suitability[site.row, site.col])
        suitability_scaled = (suitability - suitability_min) / suitability_range
        visit_probability = site_visit_probability(
            site.region,
            suitability_scaled,
            observation_config.survey,
        )
        for time_index in survey_times:
            time_scaled = time_index / max(truth_result.diagnostics.simulation_horizon, 1)
            time_probability = min(0.95, max(0.20, visit_probability * (0.90 + 0.12 * time_scaled)))
            if float(rng.random()) > time_probability:
                continue
            visited_site_times.add((site.site_id, time_index))
            for replicate in range(1, observation_config.survey.replicate_visits + 1):
                visit_id_index += 1
                effort = visit_effort(site.region, time_scaled, observation_config.survey, rng)
                visit_id = f"visit_{visit_id_index:06d}"
                abundance = float(truth_result.prey_abundance[time_index, site.row, site.col])
                observed_count = observed_response_count(
                    abundance,
                    effort,
                    observation_config.detection,
                    rng,
                )
                visit_rows.append(
                    VisitRow(
                        visit_id=visit_id,
                        site_id=site.site_id,
                        cell_id=site.cell_id,
                        time_index=time_index,
                        visit_replicate=replicate,
                        effort=effort,
                        region=site.region,
                    )
                )
                observation_rows.append(
                    ObservationRow(
                        visit_id=visit_id,
                        site_id=site.site_id,
                        cell_id=site.cell_id,
                        time_index=time_index,
                        visit_replicate=replicate,
                        effort=effort,
                        observed_count=observed_count,
                        detected=observed_count > 0,
                    )
                )

    diagnostics = build_observation_diagnostics(
        truth_result,
        survey_times,
        visit_rows=tuple(visit_rows),
        observation_rows=tuple(observation_rows),
        visited_site_time_count=len(visited_site_times),
    )
    return SynthSmallObservationResult(
        config=observation_config,
        truth=truth_result,
        site_rows=site_rows,
        visit_rows=tuple(visit_rows),
        observation_rows=tuple(observation_rows),
        evaluation_truth_rows=evaluation_truth_rows,
        diagnostics=diagnostics,
    )


def inspect_synth_small_observation_artifacts(
    artifact_dir: str | PathLike[str],
    *,
    output_dir: str | PathLike[str] | None = None,
) -> SynthSmallObservationInspectionResult:
    bundle = load_synth_small_observation_artifacts(artifact_dir)
    inspection_dir = (
        Path(output_dir) if output_dir is not None else bundle.artifact_dir / "inspection"
    )
    inspection_dir.mkdir(parents=True, exist_ok=True)

    checks = verify_observation_bundle(bundle)
    summary_rows = build_observation_summary_rows(bundle)
    smoke_payload = recoverability_smoke_payload(bundle)
    verification_path = inspection_dir / "verification.json"
    observation_summary_path = inspection_dir / "observation_summary.csv"
    recoverability_smoke_path = inspection_dir / "recoverability_smoke.json"
    report_path = inspection_dir / "report.md"

    result = SynthSmallObservationInspectionResult(
        artifact_dir=bundle.artifact_dir,
        output_dir=inspection_dir,
        verification_checks=checks,
        observation_summary_rows=summary_rows,
        recoverability_smoke=smoke_payload,
        verification_path=verification_path,
        observation_summary_path=observation_summary_path,
        recoverability_smoke_path=recoverability_smoke_path,
        report_path=report_path,
    )

    verification_path.write_text(
        dumps(result.verification_payload(), indent=2) + "\n",
        encoding="utf-8",
    )
    write_summary_rows(summary_rows, observation_summary_path)
    recoverability_smoke_path.write_text(
        dumps(smoke_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(render_observation_report(bundle, result), encoding="utf-8")
    return result


def validate_observation_config(config: SynthSmallObservationConfig) -> None:
    if config.survey.seed < 0:
        raise ValueError("observation seed must be non-negative")
    if config.survey.survey_interval <= 0:
        raise ValueError("survey_interval must be positive")
    if config.survey.replicate_visits <= 0:
        raise ValueError("replicate_visits must be positive")
    if not 0.0 < config.survey.base_visit_probability <= 1.0:
        raise ValueError("base_visit_probability must lie in (0, 1]")
    if config.survey.base_effort <= 0.0:
        raise ValueError("base_effort must be positive")
    if config.survey.effort_noise_sigma < 0.0:
        raise ValueError("effort_noise_sigma must be non-negative")
    if config.detection.count_scale <= 0.0:
        raise ValueError("count_scale must be positive")
    if config.detection.detection_half_saturation <= 0.0:
        raise ValueError("detection_half_saturation must be positive")


def build_survey_times(simulation_horizon: int, survey_interval: int) -> tuple[int, ...]:
    times = list(range(0, simulation_horizon + 1, survey_interval))
    if times[-1] != simulation_horizon:
        times.append(simulation_horizon)
    return tuple(times)


def build_site_rows(result: SynthSmallPredatorTruthResult) -> tuple[SiteRow, ...]:
    rows: list[SiteRow] = []
    for cell_id, (row, col) in enumerate(result.domain.coordinates.tolist()):
        rows.append(
            SiteRow(
                site_id=f"site_{cell_id:03d}",
                cell_id=cell_id,
                row=int(row),
                col=int(col),
                region=region_for_col(int(col), result.domain.cols),
                front_band=front_band_for_col(int(col), result.domain.cols),
            )
        )
    return tuple(rows)


def build_evaluation_truth_rows(
    result: SynthSmallPredatorTruthResult,
    site_rows: tuple[SiteRow, ...],
) -> tuple[EvaluationTruthRow, ...]:
    rows: list[EvaluationTruthRow] = []
    for site in site_rows:
        true_extirpation_raw = float(result.true_extirpation[site.row, site.col])
        extirpation_lag_raw = float(result.extirpation_lag[site.row, site.col])
        true_extirpation = None if np.isnan(true_extirpation_raw) else true_extirpation_raw
        extirpation_lag = None if np.isnan(extirpation_lag_raw) else extirpation_lag_raw
        rows.append(
            EvaluationTruthRow(
                site_id=site.site_id,
                cell_id=site.cell_id,
                row=site.row,
                col=site.col,
                driver_arrival=int(result.driver_arrival[site.row, site.col]),
                true_extirpation=true_extirpation,
                extirpation_lag=extirpation_lag,
                extirpated_by_end=true_extirpation is not None,
                initial_abundance=float(result.initial_abundance[site.row, site.col]),
                final_abundance=float(result.final_abundance[site.row, site.col]),
            )
        )
    return tuple(rows)


def site_visit_probability(
    region: str,
    suitability_scaled: float,
    config: ObservationSurveyConfig,
) -> float:
    region_bonus = {
        "west": config.west_visit_bonus,
        "central": config.central_visit_bonus,
        "east": config.east_visit_bonus,
    }[region]
    probability = (
        config.base_visit_probability
        + region_bonus
        + config.suitability_visit_weight * (suitability_scaled - 0.5)
    )
    return float(np.clip(probability, 0.15, 0.95))


def visit_effort(
    region: str,
    time_scaled: float,
    config: ObservationSurveyConfig,
    rng: np.random.Generator,
) -> float:
    region_adjustment = {"west": 0.10, "central": 0.0, "east": -0.06}[region]
    time_adjustment = 0.12 * time_scaled
    noise = float(rng.lognormal(mean=0.0, sigma=config.effort_noise_sigma))
    effort = (config.base_effort + region_adjustment + time_adjustment) * noise
    return max(0.20, effort)


def observed_response_count(
    abundance: float,
    effort: float,
    config: ObservationDetectionConfig,
    rng: np.random.Generator,
) -> int:
    intensity = (
        effort
        * config.count_scale
        * max(abundance, 0.0)
        / (config.detection_half_saturation + max(abundance, 0.0))
    )
    return int(rng.poisson(intensity))


def build_observation_diagnostics(
    truth: SynthSmallPredatorTruthResult,
    survey_times: tuple[int, ...],
    *,
    visit_rows: tuple[VisitRow, ...],
    observation_rows: tuple[ObservationRow, ...],
    visited_site_time_count: int,
) -> ObservationDiagnostics:
    efforts = [row.effort for row in visit_rows]
    counts = [row.observed_count for row in observation_rows]
    detections = [row.detected for row in observation_rows]
    return ObservationDiagnostics(
        simulation_horizon=truth.diagnostics.simulation_horizon,
        survey_times=survey_times,
        scheduled_site_time_count=truth.domain.cell_count * len(survey_times),
        visited_site_time_count=visited_site_time_count,
        total_visits=len(visit_rows),
        unique_sites_visited=len({row.site_id for row in visit_rows}),
        observation_count=len(observation_rows),
        detection_count=sum(int(value) for value in detections),
        mean_effort=float(np.mean(efforts)) if efforts else float("nan"),
        mean_observed_count=float(np.mean(counts)) if counts else float("nan"),
    )


def write_synth_small_observation_artifacts(
    result: SynthSmallObservationResult,
    output_dir: str | PathLike[str],
) -> tuple[Path, ...]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    observation_config_path = target_dir / "observation_config.json"
    truth_reference_path = target_dir / "truth_reference.json"
    sites_path = target_dir / "sites.csv"
    visits_path = target_dir / "visits.csv"
    observations_path = target_dir / "observations.csv"
    evaluation_truth_path = target_dir / "evaluation_truth.csv"

    observation_config_path.write_text(
        dumps(
            {
                "config": result.config.to_dict(),
                "diagnostics": result.diagnostics.to_dict(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    truth_reference_path.write_text(
        dumps(truth_reference_payload(result), indent=2) + "\n",
        encoding="utf-8",
    )
    write_dataclass_csv(SITE_COLUMNS, (row.to_csv_row() for row in result.site_rows), sites_path)
    write_dataclass_csv(VISIT_COLUMNS, (row.to_csv_row() for row in result.visit_rows), visits_path)
    write_dataclass_csv(
        OBSERVATION_COLUMNS,
        (row.to_csv_row() for row in result.observation_rows),
        observations_path,
    )
    write_dataclass_csv(
        EVALUATION_TRUTH_COLUMNS,
        (row.to_csv_row() for row in result.evaluation_truth_rows),
        evaluation_truth_path,
    )
    return (
        observation_config_path,
        truth_reference_path,
        sites_path,
        visits_path,
        observations_path,
        evaluation_truth_path,
    )


def truth_reference_payload(result: SynthSmallObservationResult) -> dict[str, Any]:
    extirpated_count = sum(row.extirpated_by_end for row in result.evaluation_truth_rows)
    return {
        "source": "default_synth_small_predator_truth",
        "truth_artifact_dir": result.config.truth_artifact_dir,
        "evaluation_truth_file": "evaluation_truth.csv",
        "analyst_facing_tables": list(ANALYST_FACING_FILES),
        "forbidden_analyst_columns": sorted(FORBIDDEN_ANALYST_COLUMNS),
        "note": (
            "Predator arrival, predator pressure, true extirpation, and latent "
            "abundance are withheld from analyst-facing observation tables."
        ),
        "truth_summary": {
            "simulation_horizon": result.truth.diagnostics.simulation_horizon,
            "cell_count": result.truth.domain.cell_count,
            "extirpated_count": extirpated_count,
            "surviving_count": result.truth.domain.cell_count - extirpated_count,
            "extirpated_fraction": extirpated_count / result.truth.domain.cell_count,
        },
    }


def load_synth_small_observation_artifacts(
    artifact_dir: str | PathLike[str],
) -> LoadedSynthSmallObservationBundle:
    bundle_dir = Path(artifact_dir)
    missing = [name for name in REQUIRED_OBSERVATION_FILES if not (bundle_dir / name).exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(
            f"missing required synth-small observation artifact files: {missing_text}"
        )
    return LoadedSynthSmallObservationBundle(
        artifact_dir=bundle_dir,
        observation_config=read_json(bundle_dir / "observation_config.json"),
        truth_reference=read_json(bundle_dir / "truth_reference.json"),
        sites=read_csv_rows(bundle_dir / "sites.csv"),
        visits=read_csv_rows(bundle_dir / "visits.csv"),
        observations=read_csv_rows(bundle_dir / "observations.csv"),
        evaluation_truth=read_csv_rows(bundle_dir / "evaluation_truth.csv"),
    )


def verify_observation_bundle(
    bundle: LoadedSynthSmallObservationBundle,
) -> tuple[ObservationVerificationCheck, ...]:
    schema_valid, schema_details = schema_check_details(bundle)
    analyst_clean, analyst_details = analyst_exclusion_details(bundle)
    relationship_valid, relationship_details = visit_observation_relationship_details(bundle)
    observation_values_valid, observation_values_details = observation_value_details(bundle)
    effort_time_valid, effort_time_details = effort_time_details_for(bundle)
    evaluation_valid, evaluation_details = evaluation_truth_alignment_details(bundle)
    coverage_valid, coverage_details = coverage_details_for(bundle)
    return (
        ObservationVerificationCheck(
            name="schema",
            passed=schema_valid,
            message="expected required observation bundle CSV schemas",
            details=schema_details,
        ),
        ObservationVerificationCheck(
            name="analyst_truth_exclusion",
            passed=analyst_clean,
            message="expected analyst-facing tables to exclude predator-truth columns",
            details=analyst_details,
        ),
        ObservationVerificationCheck(
            name="visit_observation_relationship",
            passed=relationship_valid,
            message="expected visits and observations to have a one-to-one visit_id relation",
            details=relationship_details,
        ),
        ObservationVerificationCheck(
            name="observation_values",
            passed=observation_values_valid,
            message=(
                "expected non-negative integer observed counts and binary detection "
                "matching observed_count > 0"
            ),
            details=observation_values_details,
        ),
        ObservationVerificationCheck(
            name="effort_time_bounds",
            passed=effort_time_valid,
            message="expected finite positive effort and times within the simulation horizon",
            details=effort_time_details,
        ),
        ObservationVerificationCheck(
            name="evaluation_truth_alignment",
            passed=evaluation_valid,
            message="expected evaluation truth rows to align with the site frame",
            details=evaluation_details,
        ),
        ObservationVerificationCheck(
            name="coverage_signal",
            passed=coverage_valid,
            message="expected observations in early and late survey windows",
            details=coverage_details,
        ),
    )


def build_observation_summary_rows(
    bundle: LoadedSynthSmallObservationBundle,
) -> tuple[ObservationSummaryRow, ...]:
    observations = bundle.observations
    visits = bundle.visits
    total_observations = len(observations)
    detected_count = sum(parse_bool(row["detected"]) for row in observations)
    counts = [parse_int(row["observed_count"]) for row in observations]
    efforts = [parse_float(row["effort"]) for row in visits]
    config = bundle.observation_config.get("config", {})
    diagnostics = bundle.observation_config.get("diagnostics", {})
    rows = [
        ObservationSummaryRow("design", "seed", stringify_nested(config, ("survey", "seed"))),
        ObservationSummaryRow(
            "design",
            "survey_interval",
            stringify_nested(config, ("survey", "survey_interval")),
        ),
        ObservationSummaryRow(
            "design",
            "replicate_visits",
            stringify_nested(config, ("survey", "replicate_visits")),
        ),
        ObservationSummaryRow(
            "coverage",
            "simulation_horizon",
            stringify_nested(diagnostics, ("simulation_horizon",)),
        ),
        ObservationSummaryRow(
            "coverage",
            "scheduled_site_time_count",
            stringify_nested(diagnostics, ("scheduled_site_time_count",)),
        ),
        ObservationSummaryRow(
            "coverage",
            "visited_site_time_count",
            stringify_nested(diagnostics, ("visited_site_time_count",)),
        ),
        ObservationSummaryRow("coverage", "site_count", str(len(bundle.sites))),
        ObservationSummaryRow("coverage", "visit_count", str(len(visits))),
        ObservationSummaryRow("coverage", "observation_count", str(total_observations)),
        ObservationSummaryRow(
            "response",
            "detection_rate",
            stringify_float(detected_count / max(total_observations, 1)),
        ),
        ObservationSummaryRow(
            "response",
            "mean_observed_count",
            stringify_float(float(np.mean(counts)) if counts else float("nan")),
        ),
        ObservationSummaryRow(
            "effort",
            "mean_effort",
            stringify_float(float(np.mean(efforts)) if efforts else float("nan")),
        ),
    ]
    rows.extend(region_summary_rows(observations))
    rows.extend(time_window_summary_rows(observations, simulation_horizon_from_bundle(bundle)))
    return tuple(rows)


def recoverability_smoke_payload(bundle: LoadedSynthSmallObservationBundle) -> dict[str, Any]:
    metrics = compute_recoverability_smoke_metrics(bundle)
    finite = all(np.isfinite(value) for value in metrics.values())
    passed = bool(
        finite
        and metrics["pre_driver_detection_rate"] > metrics["post_driver_detection_rate"]
        and metrics["late_surviving_detection_rate"] > metrics["late_extirpated_detection_rate"]
        and metrics["late_detection_auc"] > 0.60
    )
    return {
        "passed": passed,
        "metrics": {name: float(value) for name, value in metrics.items()},
        "interpretation": (
            "Smoke metrics indicate basic response signal but do not fit the "
            "process model or prove parameter identifiability."
        ),
        "limits": [
            "Uses hidden truth only for evaluation.",
            "Does not estimate predator arrival, pressure, or model parameters.",
            "Thresholds are deliberately weak and local to this synthetic pilot.",
        ],
    }


def compute_recoverability_smoke_metrics(
    bundle: LoadedSynthSmallObservationBundle,
) -> dict[str, float]:
    truth_by_site = truth_by_site_id(bundle)
    pre_detected: list[bool] = []
    post_detected: list[bool] = []
    late_by_site: dict[str, list[bool]] = {}
    horizon = simulation_horizon_from_bundle(bundle)
    late_start = int(np.ceil(0.75 * horizon))
    for row in bundle.observations:
        site_truth = truth_by_site[row["site_id"]]
        time_index = parse_int(row["time_index"])
        detected = parse_bool(row["detected"])
        driver_arrival = parse_float(site_truth["driver_arrival"])
        if time_index < driver_arrival:
            pre_detected.append(detected)
        else:
            post_detected.append(detected)
        if time_index >= late_start:
            late_by_site.setdefault(row["site_id"], []).append(detected)

    extirpated_late_rates: list[float] = []
    surviving_late_rates: list[float] = []
    labels: list[bool] = []
    scores: list[float] = []
    for site_id, detections in late_by_site.items():
        if not detections:
            continue
        late_rate = sum(int(value) for value in detections) / len(detections)
        extirpated = parse_bool(truth_by_site[site_id]["extirpated_by_end"])
        labels.append(extirpated)
        scores.append(1.0 - late_rate)
        if extirpated:
            extirpated_late_rates.append(late_rate)
        else:
            surviving_late_rates.append(late_rate)

    pre_rate = bool_rate(pre_detected)
    post_rate = bool_rate(post_detected)
    late_extirpated_rate = float(np.mean(extirpated_late_rates))
    late_surviving_rate = float(np.mean(surviving_late_rates))
    return {
        "pre_driver_detection_rate": pre_rate,
        "post_driver_detection_rate": post_rate,
        "pre_post_detection_drop": pre_rate - post_rate,
        "late_extirpated_detection_rate": late_extirpated_rate,
        "late_surviving_detection_rate": late_surviving_rate,
        "late_surviving_minus_extirpated_detection_rate": (
            late_surviving_rate - late_extirpated_rate
        ),
        "late_detection_auc": auc_for_binary_labels(labels, scores),
        "late_site_count": float(len(labels)),
        "extirpated_late_site_count": float(len(extirpated_late_rates)),
        "surviving_late_site_count": float(len(surviving_late_rates)),
    }


def schema_check_details(bundle: LoadedSynthSmallObservationBundle) -> tuple[bool, dict[str, Any]]:
    expected = {
        "sites.csv": set(SITE_COLUMNS),
        "visits.csv": set(VISIT_COLUMNS),
        "observations.csv": set(OBSERVATION_COLUMNS),
        "evaluation_truth.csv": set(EVALUATION_TRUTH_COLUMNS),
    }
    actual = {
        "sites.csv": csv_columns(bundle.sites),
        "visits.csv": csv_columns(bundle.visits),
        "observations.csv": csv_columns(bundle.observations),
        "evaluation_truth.csv": csv_columns(bundle.evaluation_truth),
    }
    missing = {
        name: sorted(expected[name] - actual[name])
        for name in expected
        if not expected[name].issubset(actual[name])
    }
    return not missing, {"missing_columns": missing, "actual_columns": sorted_columns(actual)}


def analyst_exclusion_details(
    bundle: LoadedSynthSmallObservationBundle,
) -> tuple[bool, dict[str, Any]]:
    actual = {
        "sites.csv": sorted(csv_columns(bundle.sites) & FORBIDDEN_ANALYST_COLUMNS),
        "visits.csv": sorted(csv_columns(bundle.visits) & FORBIDDEN_ANALYST_COLUMNS),
        "observations.csv": sorted(csv_columns(bundle.observations) & FORBIDDEN_ANALYST_COLUMNS),
    }
    offenders = {name: columns for name, columns in actual.items() if columns}
    return not offenders, {"forbidden_columns_found": offenders}


def visit_observation_relationship_details(
    bundle: LoadedSynthSmallObservationBundle,
) -> tuple[bool, dict[str, Any]]:
    visit_ids = [row.get("visit_id", "") for row in bundle.visits]
    observation_ids = [row.get("visit_id", "") for row in bundle.observations]
    duplicate_visit_ids = sorted(duplicates(visit_ids))
    duplicate_observation_ids = sorted(duplicates(observation_ids))
    missing_from_observations = sorted(set(visit_ids) - set(observation_ids))
    missing_from_visits = sorted(set(observation_ids) - set(visit_ids))
    passed = not (
        duplicate_visit_ids
        or duplicate_observation_ids
        or missing_from_observations
        or missing_from_visits
        or len(visit_ids) != len(observation_ids)
    )
    return passed, {
        "visit_count": len(visit_ids),
        "observation_count": len(observation_ids),
        "duplicate_visit_ids": duplicate_visit_ids[:10],
        "duplicate_observation_ids": duplicate_observation_ids[:10],
        "missing_from_observations": missing_from_observations[:10],
        "missing_from_visits": missing_from_visits[:10],
    }


def observation_value_details(
    bundle: LoadedSynthSmallObservationBundle,
) -> tuple[bool, dict[str, Any]]:
    bad_rows: list[dict[str, Any]] = []
    for row_index, row in enumerate(bundle.observations):
        try:
            count = parse_int(row["observed_count"])
            detected = parse_bool(row["detected"])
        except (KeyError, ValueError) as exc:
            bad_rows.append({"row_index": row_index, "reason": str(exc)})
            continue
        if count < 0 or detected != (count > 0):
            bad_rows.append(
                {
                    "row_index": row_index,
                    "observed_count": count,
                    "detected": detected,
                }
            )
    return not bad_rows, {"bad_rows": bad_rows[:10], "bad_row_count": len(bad_rows)}


def effort_time_details_for(
    bundle: LoadedSynthSmallObservationBundle,
) -> tuple[bool, dict[str, Any]]:
    horizon = simulation_horizon_from_bundle(bundle)
    bad_rows: list[dict[str, Any]] = []
    for table_name, rows in (
        ("visits.csv", bundle.visits),
        ("observations.csv", bundle.observations),
    ):
        for row_index, row in enumerate(rows):
            try:
                effort = parse_float(row["effort"])
                time_index = parse_int(row["time_index"])
            except (KeyError, ValueError) as exc:
                bad_rows.append({"table": table_name, "row_index": row_index, "reason": str(exc)})
                continue
            if not np.isfinite(effort) or effort <= 0.0 or time_index < 0 or time_index > horizon:
                bad_rows.append(
                    {
                        "table": table_name,
                        "row_index": row_index,
                        "effort": effort,
                        "time_index": time_index,
                    }
                )
    return not bad_rows, {
        "simulation_horizon": horizon,
        "bad_rows": bad_rows[:10],
        "bad_row_count": len(bad_rows),
    }


def evaluation_truth_alignment_details(
    bundle: LoadedSynthSmallObservationBundle,
) -> tuple[bool, dict[str, Any]]:
    site_ids = {row.get("site_id", "") for row in bundle.sites}
    truth_ids = {row.get("site_id", "") for row in bundle.evaluation_truth}
    duplicate_truth_ids = sorted(
        duplicates([row.get("site_id", "") for row in bundle.evaluation_truth])
    )
    missing_truth = sorted(site_ids - truth_ids)
    extra_truth = sorted(truth_ids - site_ids)
    bad_truth_rows: list[dict[str, Any]] = []
    for row_index, row in enumerate(bundle.evaluation_truth):
        try:
            parse_float(row["driver_arrival"])
            parse_optional_float(row["true_extirpation"])
            parse_optional_float(row["extirpation_lag"])
            parse_bool(row["extirpated_by_end"])
        except (KeyError, ValueError) as exc:
            bad_truth_rows.append({"row_index": row_index, "reason": str(exc)})
    passed = not (duplicate_truth_ids or missing_truth or extra_truth or bad_truth_rows)
    return passed, {
        "site_count": len(site_ids),
        "truth_row_count": len(bundle.evaluation_truth),
        "duplicate_truth_ids": duplicate_truth_ids[:10],
        "missing_truth": missing_truth[:10],
        "extra_truth": extra_truth[:10],
        "bad_truth_rows": bad_truth_rows[:10],
        "bad_truth_row_count": len(bad_truth_rows),
    }


def coverage_details_for(
    bundle: LoadedSynthSmallObservationBundle,
) -> tuple[bool, dict[str, Any]]:
    horizon = simulation_horizon_from_bundle(bundle)
    early_limit = int(np.floor(0.25 * horizon))
    late_start = int(np.ceil(0.75 * horizon))
    times = [parse_int(row["time_index"]) for row in bundle.observations]
    early_count = sum(time <= early_limit for time in times)
    late_count = sum(time >= late_start for time in times)
    unique_sites = len({row["site_id"] for row in bundle.observations})
    return bool(early_count > 0 and late_count > 0 and unique_sites > 0), {
        "simulation_horizon": horizon,
        "early_limit": early_limit,
        "late_start": late_start,
        "early_observation_count": early_count,
        "late_observation_count": late_count,
        "unique_observed_sites": unique_sites,
    }


def region_summary_rows(rows: tuple[dict[str, str], ...]) -> tuple[ObservationSummaryRow, ...]:
    output: list[ObservationSummaryRow] = []
    for region in ("west", "central", "east"):
        region_rows = [row for row in rows if row.get("region") == region]
        if not region_rows:
            continue
        detection_rate = sum(parse_bool(row["detected"]) for row in region_rows) / len(region_rows)
        mean_count = float(np.mean([parse_int(row["observed_count"]) for row in region_rows]))
        output.append(
            ObservationSummaryRow(
                "region_response", f"{region}_detection_rate", stringify_float(detection_rate)
            )
        )
        output.append(
            ObservationSummaryRow(
                "region_response", f"{region}_mean_count", stringify_float(mean_count)
            )
        )
    return tuple(output)


def time_window_summary_rows(
    rows: tuple[dict[str, str], ...],
    horizon: int,
) -> tuple[ObservationSummaryRow, ...]:
    early_limit = int(np.floor(0.25 * horizon))
    late_start = int(np.ceil(0.75 * horizon))
    windows = {
        "early": [row for row in rows if parse_int(row["time_index"]) <= early_limit],
        "late": [row for row in rows if parse_int(row["time_index"]) >= late_start],
    }
    output: list[ObservationSummaryRow] = []
    for name, window_rows in windows.items():
        if not window_rows:
            detection_rate = float("nan")
            mean_count = float("nan")
        else:
            detection_rate = sum(parse_bool(row["detected"]) for row in window_rows) / len(
                window_rows
            )
            mean_count = float(np.mean([parse_int(row["observed_count"]) for row in window_rows]))
        output.append(
            ObservationSummaryRow(
                "time_response", f"{name}_detection_rate", stringify_float(detection_rate)
            )
        )
        output.append(
            ObservationSummaryRow(
                "time_response", f"{name}_mean_count", stringify_float(mean_count)
            )
        )
    return tuple(output)


def render_observation_report(
    bundle: LoadedSynthSmallObservationBundle,
    result: SynthSmallObservationInspectionResult,
) -> str:
    checks = {check.name: check for check in result.verification_checks}
    metrics = result.recoverability_smoke["metrics"]
    config = bundle.observation_config.get("config", {})
    diagnostics = bundle.observation_config.get("diagnostics", {})
    visited_site_time_count = stringify_nested(diagnostics, ("visited_site_time_count",))
    early_detection_rate = summary_value(result, "time_response", "early_detection_rate")
    lines = [
        "# Synth-Small Observation Inspection Report",
        "",
        "## Verification",
        "",
        f"- Overall status: `{'passed' if result.passed else 'failed'}`",
        (
            "- Analyst-facing predator-truth exclusion: "
            f"`{'passed' if checks['analyst_truth_exclusion'].passed else 'failed'}`"
        ),
        "",
        "## Sampling Design",
        "",
        f"- Seed: `{stringify_nested(config, ('survey', 'seed'))}`",
        f"- Survey interval: `{stringify_nested(config, ('survey', 'survey_interval'))}`",
        f"- Replicate visits: `{stringify_nested(config, ('survey', 'replicate_visits'))}`",
        f"- Survey times: `{stringify_nested(diagnostics, ('survey_times',))}`",
        f"- Candidate sites: `{len(bundle.sites)}`",
        f"- Realized visits: `{len(bundle.visits)}`",
        "",
        "## Detection And Effort",
        "",
        f"- Count scale: `{stringify_nested(config, ('detection', 'count_scale'))}`",
        (
            "- Detection half-saturation: "
            f"`{stringify_nested(config, ('detection', 'detection_half_saturation'))}`"
        ),
        f"- Mean effort: `{summary_value(result, 'effort', 'mean_effort')}`",
        "",
        "## Coverage And Response",
        "",
        f"- Visited site-time cells: `{visited_site_time_count}`",
        f"- Observations: `{len(bundle.observations)}`",
        f"- Detection rate: `{summary_value(result, 'response', 'detection_rate')}`",
        f"- Early detection rate: `{early_detection_rate}`",
        f"- Late detection rate: `{summary_value(result, 'time_response', 'late_detection_rate')}`",
        "",
        "## Recoverability Smoke Test",
        "",
        f"- Status: `{'passed' if result.recoverability_smoke['passed'] else 'failed'}`",
        f"- Pre-driver detection rate: `{metrics['pre_driver_detection_rate']:.6g}`",
        f"- Post-driver detection rate: `{metrics['post_driver_detection_rate']:.6g}`",
        f"- Late extirpated detection rate: `{metrics['late_extirpated_detection_rate']:.6g}`",
        f"- Late surviving detection rate: `{metrics['late_surviving_detection_rate']:.6g}`",
        f"- Late-detection AUC: `{metrics['late_detection_auc']:.6g}`",
        "",
        "## Interpretation Limits",
        "",
        (
            "The smoke test uses hidden truth only for evaluation. It shows "
            "whether the noisy response observations retain basic signal, but "
            "it does not fit the model or establish parameter identifiability."
        ),
        "",
    ]
    return "\n".join(lines)


def write_dataclass_csv(
    header: tuple[str, ...],
    rows: Any,
    output_path: Path,
) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(header)
        csv_writer.writerows(rows)


def write_summary_rows(rows: tuple[ObservationSummaryRow, ...], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(("section", "metric", "value"))
        for row in rows:
            csv_writer.writerow(row.to_csv_row())


def read_json(path: Path) -> dict[str, Any]:
    payload = loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return cast(dict[str, Any], payload)


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def region_for_col(col: int, cols: int) -> str:
    if col < cols // 3:
        return "west"
    if col < (2 * cols) // 3:
        return "central"
    return "east"


def front_band_for_col(col: int, cols: int) -> str:
    if col < 5:
        return "west_band"
    if col >= cols - 5:
        return "east_band"
    return "middle_band"


def csv_columns(rows: tuple[dict[str, str], ...]) -> set[str]:
    if not rows:
        return set()
    return set(rows[0])


def sorted_columns(columns: dict[str, set[str]]) -> dict[str, list[str]]:
    return {name: sorted(values) for name, values in columns.items()}


def duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicated: set[str] = set()
    for value in values:
        if value in seen:
            duplicated.add(value)
        seen.add(value)
    return duplicated


def simulation_horizon_from_bundle(bundle: LoadedSynthSmallObservationBundle) -> int:
    diagnostics = bundle.observation_config.get("diagnostics", {})
    if not isinstance(diagnostics, dict):
        return -1
    value = diagnostics.get("simulation_horizon", -1)
    return int(value) if isinstance(value, int | float) else -1


def truth_by_site_id(bundle: LoadedSynthSmallObservationBundle) -> dict[str, dict[str, str]]:
    return {row["site_id"]: row for row in bundle.evaluation_truth}


def summary_value(
    result: SynthSmallObservationInspectionResult,
    section: str,
    metric: str,
) -> str:
    for row in result.observation_summary_rows:
        if row.section == section and row.metric == metric:
            return row.value
    return "NA"


def stringify_nested(payload: object, path: tuple[str, ...]) -> str:
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return "NA"
        current = current[key]
    return str(current)


def bool_rate(values: list[bool]) -> float:
    if not values:
        return float("nan")
    return sum(int(value) for value in values) / len(values)


def auc_for_binary_labels(labels: list[bool], scores: list[float]) -> float:
    positive_scores = [score for label, score in zip(labels, scores, strict=True) if label]
    negative_scores = [score for label, score in zip(labels, scores, strict=True) if not label]
    if not positive_scores or not negative_scores:
        return float("nan")
    wins = 0.0
    comparisons = 0
    for positive_score in positive_scores:
        for negative_score in negative_scores:
            comparisons += 1
            if positive_score > negative_score:
                wins += 1.0
            elif positive_score == negative_score:
                wins += 0.5
    return wins / comparisons


def parse_int(value: str) -> int:
    return int(value)


def parse_float(value: str) -> float:
    return float(value)


def parse_optional_float(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def parse_bool(value: str) -> bool:
    if value == "1":
        return True
    if value == "0":
        return False
    raise ValueError(f"expected binary value 0/1, got {value!r}")


def stringify_bool(value: bool) -> str:
    return "1" if value else "0"


def stringify_float(value: float) -> str:
    return f"{value:.12g}"


def stringify_nullable_float(value: float | None) -> str:
    if value is None:
        return ""
    return stringify_float(value)
