"""Tests for instancegenerator module."""

import pytest

from adventuregame.instancegenerator import AdventureGameInstanceGenerator


class TestAdventureGameInstanceGenerator:
    """Test cases for AdventureGameInstanceGenerator class."""

    def test_generator_instantiation(self):
        """Test that instance generator can be instantiated."""
        generator = AdventureGameInstanceGenerator()
        assert generator is not None

    def test_generator_has_generate_instances_method(self):
        """Test that generator has generate_instances method."""
        generator = AdventureGameInstanceGenerator()
        assert hasattr(generator, "generate_instances")
        assert callable(getattr(generator, "generate_instances"))

    def test_generator_has_on_generate_method(self):
        """Test that generator has on_generate method."""
        generator = AdventureGameInstanceGenerator()
        assert hasattr(generator, "on_generate")
        assert callable(getattr(generator, "on_generate"))
