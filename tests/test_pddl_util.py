"""Tests for PDDL parsing utilities."""

import pytest

from adventuregame.resources.pddl_util import PDDLActionTransformer


class TestPDDLActionTransformer:
    """Test cases for PDDLActionTransformer class."""

    def test_transformer_instantiation(self):
        """Test that PDDLActionTransformer can be instantiated."""
        transformer = PDDLActionTransformer()
        assert transformer is not None

    def test_parameters_method_exists(self):
        """Test that parameters method exists."""
        transformer = PDDLActionTransformer()
        assert hasattr(transformer, "parameters")
        assert callable(getattr(transformer, "parameters"))

    def test_precondition_method_exists(self):
        """Test that precondition method exists."""
        transformer = PDDLActionTransformer()
        assert hasattr(transformer, "precondition")
        assert callable(getattr(transformer, "precondition"))

    def test_effect_method_exists(self):
        """Test that effect method exists."""
        transformer = PDDLActionTransformer()
        assert hasattr(transformer, "effect")
        assert callable(getattr(transformer, "effect"))

    def test_action_method_exists(self):
        """Test that action method exists."""
        transformer = PDDLActionTransformer()
        assert hasattr(transformer, "action")
        assert callable(getattr(transformer, "action"))

    def test_forall_method_exists(self):
        """Test that forall method exists."""
        transformer = PDDLActionTransformer()
        assert hasattr(transformer, "forall")
        assert callable(getattr(transformer, "forall"))

    def test_when_method_exists(self):
        """Test that when method exists."""
        transformer = PDDLActionTransformer()
        assert hasattr(transformer, "when")
        assert callable(getattr(transformer, "when"))

    def test_andp_method_exists(self):
        """Test that andp method exists."""
        transformer = PDDLActionTransformer()
        assert hasattr(transformer, "andp")
        assert callable(getattr(transformer, "andp"))

    def test_orp_method_exists(self):
        """Test that orp method exists."""
        transformer = PDDLActionTransformer()
        assert hasattr(transformer, "orp")
        assert callable(getattr(transformer, "orp"))
