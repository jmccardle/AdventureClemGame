"""Pytest configuration and fixtures for AdventureGame tests."""

import json
import os
import sys
from pathlib import Path

import pytest

# Add adventuregame to path so we can import modules
ADVENTUREGAME_ROOT = Path(__file__).parent.parent / "adventuregame"
sys.path.insert(0, str(ADVENTUREGAME_ROOT))


@pytest.fixture
def sample_config():
    """Provide a sample configuration dictionary."""
    return {
        "inventory_soft_limit": 7,
        "show_curated_goals": False,
        "show_curated_prompts": False,
        "show_optimal_turns": False,
        "include_exploration_questions": False,
    }


@pytest.fixture
def sample_pddl_action():
    """Provide a sample PDDL action definition."""
    return {
        "name": "take",
        "parameters": ["?item - item", "?room - room"],
        "conditions": [
            ("at", "?item", "?room"),
            ("player-at", "?room"),
            ("not", ("in-inventory", "?item")),
        ],
        "effects": [("in-inventory", "?item"), ("not", ("at", "?item", "?room"))],
    }


@pytest.fixture
def sample_world_state():
    """Provide a sample world state for testing."""
    return {
        "facts": [
            ("at", "orange1", "kitchen"),
            ("at", "cupboard1", "kitchen"),
            ("player-at", "kitchen"),
            ("is-closed", "cupboard1"),
        ],
        "inventory": set(),
        "current_room": "kitchen",
    }


@pytest.fixture
def sample_instance_data():
    """Provide sample instance data."""
    return {
        "variant": "basic",
        "prompt": "You are in a kitchen. Your goal is to: $GOAL$",
        "initial_state": [
            "at(orange1, kitchen)",
            "at(cupboard1, kitchen)",
            "player-at(kitchen)",
            "is-closed(cupboard1)",
        ],
        "goal_state": ["in-inventory(orange1)"],
        "optimal_turns": 2,
        "max_turns": 10,
        "action_definitions": {},
        "domain_definition": {},
    }
