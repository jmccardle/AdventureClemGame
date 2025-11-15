"""
Runtime configuration for AdventureGame.

This module provides type-safe access to runtime configuration including:
- File paths
- Logging settings
- Parser settings
- Game constants
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class GrammarFiles:
    """Grammar file paths."""

    pddl_actions: str
    pddl_domain: str
    pddl_events: str
    grammar_core: str


@dataclass(frozen=True)
class Paths:
    """File system paths for the game."""

    game_module_path: Path
    resources_dir: Path
    definitions_dir: Path
    instances_dir: Path
    grammar_files: GrammarFiles


@dataclass(frozen=True)
class Logging:
    """Logging configuration."""

    level: str
    format: str


@dataclass(frozen=True)
class Parser:
    """Parser configuration."""

    action_start_rule: str
    domain_start_rule: str
    event_start_rule: str


@dataclass(frozen=True)
class Game:
    """Game constants."""

    name: str
    description: str
    command_prefix: str
    command_prefix_with_space: str


@dataclass(frozen=True)
class RuntimeConfig:
    """
    Type-safe runtime configuration.

    This configuration contains settings that control the execution environment:
    paths, logging, parser settings, and game constants.
    """

    paths: Paths
    logging: Logging
    parser: Parser
    game: Game

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "RuntimeConfig":
        """
        Load runtime configuration from JSON file.

        Args:
            config_path: Path to runtime.json. If None, uses default location.

        Returns:
            RuntimeConfig instance with type-safe access to all settings.

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if config_path is None:
            config_path = Path(__file__).parent / "runtime.json"

        try:
            with open(config_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Runtime config not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {config_path}: {e}")

        # Parse grammar files
        grammar_data = data["paths"]["grammar_files"]
        grammar_files = GrammarFiles(
            pddl_actions=grammar_data["pddl_actions"],
            pddl_domain=grammar_data["pddl_domain"],
            pddl_events=grammar_data["pddl_events"],
            grammar_core=grammar_data["grammar_core"],
        )

        # Parse paths
        paths_data = data["paths"]
        paths = Paths(
            game_module_path=Path(paths_data["game_module_path"]),
            resources_dir=Path(paths_data["resources_dir"]),
            definitions_dir=Path(paths_data["definitions_dir"]),
            instances_dir=Path(paths_data["instances_dir"]),
            grammar_files=grammar_files,
        )

        # Parse logging
        logging_data = data["logging"]
        logging = Logging(
            level=logging_data["level"],
            format=logging_data["format"],
        )

        # Parse parser
        parser_data = data["parser"]
        parser = Parser(
            action_start_rule=parser_data["action_start_rule"],
            domain_start_rule=parser_data["domain_start_rule"],
            event_start_rule=parser_data["event_start_rule"],
        )

        # Parse game
        game_data = data["game"]
        game = Game(
            name=game_data["name"],
            description=game_data["description"],
            command_prefix=game_data["command_prefix"],
            command_prefix_with_space=game_data["command_prefix_with_space"],
        )

        return cls(
            paths=paths,
            logging=logging,
            parser=parser,
            game=game,
        )


# Module-level singleton
_runtime_config: Optional[RuntimeConfig] = None


def get_runtime_config(config_path: Optional[Path] = None) -> RuntimeConfig:
    """
    Get the global runtime configuration instance.

    Args:
        config_path: Optional path to config file. Only used on first call.

    Returns:
        The global RuntimeConfig instance with type-safe access.

    Example:
        >>> config = get_runtime_config()
        >>> print(config.paths.resources_dir)
        PosixPath('resources/')
        >>> print(config.game.command_prefix)
        >
    """
    global _runtime_config
    if _runtime_config is None:
        _runtime_config = RuntimeConfig.load(config_path)
    return _runtime_config
