"""Small synthetic benchmarks for baseline module development."""

from .baseline import (
    EquilibriumDiagnostics,
    GaussianBumpConfig,
    SuitabilitySurfaceConfig,
    SynthSmallBaselineConfig,
    SynthSmallBaselineResult,
    build_synth_small_baseline,
    default_synth_small_baseline_config,
    write_synth_small_baseline_artifacts,
)

__all__ = [
    "EquilibriumDiagnostics",
    "GaussianBumpConfig",
    "SuitabilitySurfaceConfig",
    "SynthSmallBaselineConfig",
    "SynthSmallBaselineResult",
    "build_synth_small_baseline",
    "default_synth_small_baseline_config",
    "write_synth_small_baseline_artifacts",
]
