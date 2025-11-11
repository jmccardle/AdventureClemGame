"""Tests for master module."""

import pytest

from adventuregame.master import (
    AdventureGameBenchmark,
    AdventureGameMaster,
    AdventureGameScorer,
)


class TestAdventureGameMaster:
    """Test cases for AdventureGameMaster class."""

    def test_game_master_instantiation(self):
        """Test that game master can be instantiated with minimal data."""
        experiment_dict = {"name": "test_experiment"}
        game_instance = {
            "initial_state": [],
            "action_definitions": {},
            "domain_definition": {"types": [], "predicates": []},
            "goal_state": [],
            "variant": "basic",
            "prompt": "Test prompt",
            "max_turns": 10,
        }
        master = AdventureGameMaster(experiment_dict, game_instance)
        assert master is not None

    def test_game_master_has_setup_method(self):
        """Test that game master has setup method."""
        experiment_dict = {"name": "test_experiment"}
        game_instance = {
            "initial_state": [],
            "action_definitions": {},
            "domain_definition": {"types": [], "predicates": []},
            "goal_state": [],
            "variant": "basic",
            "prompt": "Test prompt",
            "max_turns": 10,
        }
        master = AdventureGameMaster(experiment_dict, game_instance)
        assert hasattr(master, "setup")
        assert callable(getattr(master, "setup"))

    def test_game_master_has_play_method(self):
        """Test that game master has play method."""
        experiment_dict = {"name": "test_experiment"}
        game_instance = {
            "initial_state": [],
            "action_definitions": {},
            "domain_definition": {"types": [], "predicates": []},
            "goal_state": [],
            "variant": "basic",
            "prompt": "Test prompt",
            "max_turns": 10,
        }
        master = AdventureGameMaster(experiment_dict, game_instance)
        assert hasattr(master, "play")
        assert callable(getattr(master, "play"))


class TestAdventureGameScorer:
    """Test cases for AdventureGameScorer class."""

    def test_scorer_instantiation(self):
        """Test that scorer can be instantiated."""
        experiment_dict = {"name": "test_experiment"}
        scorer = AdventureGameScorer(experiment_dict)
        assert scorer is not None

    def test_scorer_has_compute_scores_method(self):
        """Test that scorer has compute_scores method."""
        experiment_dict = {"name": "test_experiment"}
        scorer = AdventureGameScorer(experiment_dict)
        assert hasattr(scorer, "compute_scores")
        assert callable(getattr(scorer, "compute_scores"))


class TestAdventureGameBenchmark:
    """Test cases for AdventureGameBenchmark class."""

    def test_benchmark_instantiation(self):
        """Test that benchmark can be instantiated."""
        benchmark = AdventureGameBenchmark()
        assert benchmark is not None

    def test_benchmark_has_get_description_method(self):
        """Test that benchmark has get_description method."""
        benchmark = AdventureGameBenchmark()
        assert hasattr(benchmark, "get_description")
        assert callable(getattr(benchmark, "get_description"))

    def test_benchmark_description_is_string(self):
        """Test that benchmark description returns a string."""
        benchmark = AdventureGameBenchmark()
        description = benchmark.get_description()
        assert isinstance(description, str)
        assert len(description) > 0
