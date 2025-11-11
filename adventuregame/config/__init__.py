"""
Configuration management for AdventureGame.

This package provides type-safe, focused configuration modules that follow
separation of concerns principles:

- runtime: Paths, logging, parser settings
- experiments: Parameters for running experiments (thresholds, seeds, etc.)
- messages: User-facing message templates

Domain knowledge (actions, entities, rooms, adventure types) remains in
resources/definitions/ where it belongs.
"""

from adventuregame.config.experiments import ExperimentConfig, get_experiment_config
from adventuregame.config.messages import MessageTemplates, get_message_templates
from adventuregame.config.runtime import RuntimeConfig, get_runtime_config

__all__ = [
    "RuntimeConfig",
    "get_runtime_config",
    "ExperimentConfig",
    "get_experiment_config",
    "MessageTemplates",
    "get_message_templates",
]
