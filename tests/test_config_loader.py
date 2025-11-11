"""Tests for config_loader module."""

import json
import tempfile
from pathlib import Path

import pytest

from adventuregame.config_loader import ConfigLoader, cfg, get_config


class TestConfigLoader:
    """Test cases for ConfigLoader class."""

    def test_load_config_from_default_location(self):
        """Test that config loads from default location."""
        config = ConfigLoader()
        assert config is not None
        assert config._config is not None

    def test_load_config_from_custom_path(self):
        """Test loading config from a custom path."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp:
            test_config = {"test_key": "test_value", "nested": {"key": "value"}}
            json.dump(test_config, tmp)
            tmp_path = tmp.name

        try:
            config = ConfigLoader(tmp_path)
            assert config.get("test_key") == "test_value"
            assert config.get("nested", "key") == "value"
        finally:
            Path(tmp_path).unlink()

    def test_get_single_key(self):
        """Test getting a single configuration key."""
        config = ConfigLoader()
        result = config.get("paths")
        assert isinstance(result, dict)

    def test_get_nested_keys(self):
        """Test getting nested configuration keys."""
        config = ConfigLoader()
        result = config.get("paths", "resources_dir")
        assert result is not None

    def test_get_with_default(self):
        """Test that default value is returned for missing keys."""
        config = ConfigLoader()
        result = config.get("nonexistent_key", default="default_value")
        assert result == "default_value"

    def test_get_nested_missing_key_with_default(self):
        """Test default value for missing nested keys."""
        config = ConfigLoader()
        result = config.get("paths", "nonexistent", default="default")
        assert result == "default"

    def test_paths_property(self):
        """Test paths property returns dict."""
        config = ConfigLoader()
        assert isinstance(config.paths, dict)

    def test_game_constants_property(self):
        """Test game_constants property returns dict."""
        config = ConfigLoader()
        assert isinstance(config.game_constants, dict)

    def test_variants_property(self):
        """Test variants property returns dict."""
        config = ConfigLoader()
        assert isinstance(config.variants, dict)


class TestGlobalConfigAccess:
    """Test cases for global config access functions."""

    def test_get_config_singleton(self):
        """Test that get_config returns the same instance."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_cfg_convenience_function(self):
        """Test cfg convenience function."""
        result = cfg("paths", "resources_dir")
        assert result is not None

    def test_cfg_with_default(self):
        """Test cfg with default value."""
        result = cfg("nonexistent", default="test_default")
        assert result == "test_default"
