"""
Experiment configuration for AdventureGame.

This module provides type-safe access to experiment parameters that researchers
modify when running experiments:
- Random seeds
- Thresholds for various game mechanics
- Turn limits
- Scoring values
- Clingo solver settings
- Generation parameters
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Thresholds:
    """Threshold values for game mechanics."""

    loop_detection: int
    min_plan_history: int
    bad_plan_viability: float
    exploration_history: int
    goal_count_min: int


@dataclass(frozen=True)
class TurnLimits:
    """Turn limit configuration."""

    optimal_solver: int
    benchmark_default: int


@dataclass(frozen=True)
class Scoring:
    """Scoring values."""

    success: int
    failure: int


@dataclass(frozen=True)
class ClingoConfig:
    """Clingo solver configuration."""

    control_all_models: List[str]
    status_sat: str
    status_unsat: str
    picking_strategies: Dict[str, str]
    default_layout_generation_limit: int
    default_initial_states_per_layout: int
    default_initial_state_limit: int
    default_adventures_per_initial_state: int
    default_target_adventure_count: int
    add_floors_default: bool
    pair_exits_default: bool


@dataclass(frozen=True)
class GenerationConfig:
    """Instance generation configuration."""

    definition_methods: Dict[str, str]
    adjective_configs: Dict[str, str]
    difficulty_levels: Dict[str, str]


@dataclass(frozen=True)
class ExperimentConfig:
    """
    Type-safe experiment configuration.

    This configuration contains parameters that researchers typically modify
    when running experiments: random seeds, thresholds, turn limits, etc.
    """

    random_seed: int
    max_random_seed: int
    thresholds: Thresholds
    turn_limits: TurnLimits
    scoring: Scoring
    clingo: ClingoConfig
    generation: GenerationConfig

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "ExperimentConfig":
        """
        Load experiment configuration from JSON file.

        Args:
            config_path: Path to experiments.json. If None, uses default location.

        Returns:
            ExperimentConfig instance with type-safe access to all settings.

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if config_path is None:
            config_path = Path(__file__).parent / "experiments.json"

        try:
            with open(config_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Experiment config not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {config_path}: {e}")

        # Parse thresholds
        thresholds_data = data["thresholds"]
        thresholds = Thresholds(
            loop_detection=thresholds_data["loop_detection"],
            min_plan_history=thresholds_data["min_plan_history"],
            bad_plan_viability=thresholds_data["bad_plan_viability"],
            exploration_history=thresholds_data["exploration_history"],
            goal_count_min=thresholds_data["goal_count_min"],
        )

        # Parse turn limits
        turn_limits_data = data["turn_limits"]
        turn_limits = TurnLimits(
            optimal_solver=turn_limits_data["optimal_solver"],
            benchmark_default=turn_limits_data["benchmark_default"],
        )

        # Parse scoring
        scoring_data = data["scoring"]
        scoring = Scoring(
            success=scoring_data["success"],
            failure=scoring_data["failure"],
        )

        # Parse clingo
        clingo_data = data["clingo"]
        clingo = ClingoConfig(
            control_all_models=clingo_data["control_all_models"],
            status_sat=clingo_data["status_sat"],
            status_unsat=clingo_data["status_unsat"],
            picking_strategies=clingo_data["picking_strategies"],
            default_layout_generation_limit=clingo_data["default_layout_generation_limit"],
            default_initial_states_per_layout=clingo_data["default_initial_states_per_layout"],
            default_initial_state_limit=clingo_data["default_initial_state_limit"],
            default_adventures_per_initial_state=clingo_data[
                "default_adventures_per_initial_state"
            ],
            default_target_adventure_count=clingo_data["default_target_adventure_count"],
            add_floors_default=clingo_data["add_floors_default"],
            pair_exits_default=clingo_data["pair_exits_default"],
        )

        # Parse generation
        generation_data = data["generation"]
        generation = GenerationConfig(
            definition_methods=generation_data["definition_methods"],
            adjective_configs=generation_data["adjective_configs"],
            difficulty_levels=generation_data["difficulty_levels"],
        )

        return cls(
            random_seed=data["random_seed"],
            max_random_seed=data["max_random_seed"],
            thresholds=thresholds,
            turn_limits=turn_limits,
            scoring=scoring,
            clingo=clingo,
            generation=generation,
        )


# Module-level singleton
_experiment_config: Optional[ExperimentConfig] = None


def get_experiment_config(config_path: Optional[Path] = None) -> ExperimentConfig:
    """
    Get the global experiment configuration instance.

    Args:
        config_path: Optional path to config file. Only used on first call.

    Returns:
        The global ExperimentConfig instance with type-safe access.

    Example:
        >>> config = get_experiment_config()
        >>> print(config.random_seed)
        42
        >>> print(config.thresholds.loop_detection)
        4
    """
    global _experiment_config
    if _experiment_config is None:
        _experiment_config = ExperimentConfig.load(config_path)
    return _experiment_config
