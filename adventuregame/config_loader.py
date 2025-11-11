"""
Configuration loader for AdventureGame.

This module provides centralized access to configuration values that were
previously hardcoded throughout the codebase. All configuration is stored
in config.json and loaded once at module import time.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfigLoader:
    """Loads and provides access to configuration values."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the config loader.

        Args:
            config_path: Path to config.json. If None, uses default location.
        """
        if config_path is None:
            # Default to config.json in the same directory as this module
            config_path = Path(__file__).parent / "config.json"

        with open(config_path, "r") as f:
            self._config: Dict[str, Any] = json.load(f)

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value by path.

        Args:
            *keys: Nested keys to traverse (e.g., 'paths', 'resources_dir')
            default: Default value if key not found

        Returns:
            The configuration value or default

        Example:
            config.get('paths', 'resources_dir')  # Returns 'resources/'
        """
        current = self._config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    # Convenience properties for frequently accessed values

    @property
    def paths(self) -> Dict[str, Any]:
        """Get all path configurations."""
        return self._config.get("paths", {})

    @property
    def game_constants(self) -> Dict[str, Any]:
        """Get game constants."""
        return self._config.get("game_constants", {})

    @property
    def variants(self) -> Dict[str, Any]:
        """Get variant configurations."""
        return self._config.get("variants", {})

    @property
    def adventure_types(self) -> Dict[str, str]:
        """Get adventure type identifiers."""
        return self._config.get("adventure_types", {})

    @property
    def actions(self) -> Dict[str, Any]:
        """Get action configurations."""
        return self._config.get("actions", {})

    @property
    def entities(self) -> Dict[str, Any]:
        """Get entity configurations."""
        return self._config.get("entities", {})

    @property
    def predicates(self) -> Dict[str, Any]:
        """Get predicate definitions."""
        return self._config.get("predicates", {})

    @property
    def keys(self) -> Dict[str, str]:
        """Get dictionary key constants."""
        return self._config.get("keys", {})

    @property
    def delimiters(self) -> Dict[str, str]:
        """Get delimiter strings."""
        return self._config.get("delimiters", {})

    @property
    def template_placeholders(self) -> Dict[str, str]:
        """Get template placeholder strings."""
        return self._config.get("template_placeholders", {})

    @property
    def event_types(self) -> Dict[str, str]:
        """Get event type identifiers."""
        return self._config.get("event_types", {})

    @property
    def log_keys(self) -> Dict[str, str]:
        """Get log key constants."""
        return self._config.get("log_keys", {})

    @property
    def parse_errors(self) -> Dict[str, str]:
        """Get parse error type identifiers."""
        return self._config.get("parse_errors", {})

    @property
    def fail_types(self) -> List[str]:
        """Get list of all action failure types."""
        return self._config.get("fail_types", [])

    @property
    def plan_metrics(self) -> List[str]:
        """Get list of plan metrics to track."""
        return self._config.get("plan_metrics", [])

    @property
    def hallucination_keywords(self) -> List[str]:
        """Get list of hallucination indicator keywords."""
        return self._config.get("hallucination_keywords", [])

    @property
    def thresholds(self) -> Dict[str, Any]:
        """Get threshold values."""
        return self._config.get("thresholds", {})

    @property
    def array_indices(self) -> Dict[str, int]:
        """Get array index constants."""
        return self._config.get("array_indices", {})

    @property
    def scores(self) -> Dict[str, int]:
        """Get scoring values."""
        return self._config.get("scores", {})

    @property
    def messages(self) -> Dict[str, str]:
        """Get user-facing message templates."""
        return self._config.get("messages", {})

    @property
    def parser_settings(self) -> Dict[str, str]:
        """Get parser configuration."""
        return self._config.get("parser_settings", {})

    @property
    def clingo_settings(self) -> Dict[str, Any]:
        """Get Clingo solver settings."""
        return self._config.get("clingo_settings", {})

    @property
    def generation_settings(self) -> Dict[str, Any]:
        """Get instance generation settings."""
        return self._config.get("generation_settings", {})

    @property
    def goal_settings(self) -> Dict[str, str]:
        """Get goal-related settings."""
        return self._config.get("goal_settings", {})

    @property
    def output_settings(self) -> Dict[str, Any]:
        """Get output formatting settings."""
        return self._config.get("output_settings", {})

    @property
    def random_seeds(self) -> Dict[str, int]:
        """Get random seed configurations."""
        return self._config.get("random_seeds", {})

    @property
    def initial_counts(self) -> Dict[str, int]:
        """Get initial count values."""
        return self._config.get("initial_counts", {})


# Global singleton instance
_config_instance: Optional[ConfigLoader] = None


def get_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Get the global configuration instance.

    Args:
        config_path: Optional path to config file. Only used on first call.

    Returns:
        The global ConfigLoader instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance


# Convenience function for quick access
def cfg(*keys: str, default: Any = None) -> Any:
    """
    Quick access to configuration values.

    Args:
        *keys: Nested keys to traverse
        default: Default value if not found

    Returns:
        The configuration value

    Example:
        from config_loader import cfg
        resources_dir = cfg('paths', 'resources_dir')
    """
    return get_config().get(*keys, default=default)
