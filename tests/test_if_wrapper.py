"""Tests for if_wrapper module."""

import pytest

from adventuregame.if_wrapper import AdventureIFInterpreter


class TestAdventureIFInterpreter:
    """Test cases for AdventureIFInterpreter class."""

    def test_interpreter_instantiation_requires_game_instance(self):
        """Test that interpreter requires a game instance."""
        # This should work if we provide minimal game instance data
        minimal_instance = {
            "initial_state": [],
            "action_definitions": {},
            "domain_definition": {"types": [], "predicates": []},
            "goal_state": [],
            "variant": "basic",
        }
        interpreter = AdventureIFInterpreter(minimal_instance, "")
        assert interpreter is not None

    def test_interpreter_has_parse_action_input_method(self):
        """Test that interpreter has parse_action_input method."""
        minimal_instance = {
            "initial_state": [],
            "action_definitions": {},
            "domain_definition": {"types": [], "predicates": []},
            "goal_state": [],
            "variant": "basic",
        }
        interpreter = AdventureIFInterpreter(minimal_instance, "")
        assert hasattr(interpreter, "parse_action_input")
        assert callable(getattr(interpreter, "parse_action_input"))

    def test_interpreter_has_resolve_action_method(self):
        """Test that interpreter has resolve_action method."""
        minimal_instance = {
            "initial_state": [],
            "action_definitions": {},
            "domain_definition": {"types": [], "predicates": []},
            "goal_state": [],
            "variant": "basic",
        }
        interpreter = AdventureIFInterpreter(minimal_instance, "")
        assert hasattr(interpreter, "resolve_action")
        assert callable(getattr(interpreter, "resolve_action"))

    def test_interpreter_has_check_conditions_method(self):
        """Test that interpreter has check_conditions method."""
        minimal_instance = {
            "initial_state": [],
            "action_definitions": {},
            "domain_definition": {"types": [], "predicates": []},
            "goal_state": [],
            "variant": "basic",
        }
        interpreter = AdventureIFInterpreter(minimal_instance, "")
        assert hasattr(interpreter, "check_conditions")
        assert callable(getattr(interpreter, "check_conditions"))

    def test_interpreter_has_get_feedback_method(self):
        """Test that interpreter has get_feedback method."""
        minimal_instance = {
            "initial_state": [],
            "action_definitions": {},
            "domain_definition": {"types": [], "predicates": []},
            "goal_state": [],
            "variant": "basic",
        }
        interpreter = AdventureIFInterpreter(minimal_instance, "")
        assert hasattr(interpreter, "get_feedback")
        assert callable(getattr(interpreter, "get_feedback"))

    def test_interpreter_has_run_events_method(self):
        """Test that interpreter has run_events method."""
        minimal_instance = {
            "initial_state": [],
            "action_definitions": {},
            "domain_definition": {"types": [], "predicates": []},
            "goal_state": [],
            "variant": "basic",
        }
        interpreter = AdventureIFInterpreter(minimal_instance, "")
        assert hasattr(interpreter, "run_events")
        assert callable(getattr(interpreter, "run_events"))
