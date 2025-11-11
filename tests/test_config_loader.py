"""Tests for config system (compatibility layer)."""

from adventuregame.config.compat import CompatConfigLoader, get_config


class TestCompatConfigLoader:
    """Test cases for CompatConfigLoader class (backward compatibility)."""

    def test_load_config_from_default_location(self):
        """Test that config loads from default location."""
        config = CompatConfigLoader()
        assert config is not None

    def test_get_single_key(self):
        """Test getting a single configuration key."""
        config = CompatConfigLoader()
        result = config.get("paths")
        assert isinstance(result, dict)

    def test_get_nested_keys(self):
        """Test getting nested configuration keys."""
        config = CompatConfigLoader()
        result = config.get("paths", "resources_dir")
        assert result is not None

    def test_get_with_default(self):
        """Test that default value is returned for missing keys."""
        config = CompatConfigLoader()
        result = config.get("nonexistent_key", default="default_value")
        assert result == "default_value"

    def test_get_nested_missing_key_with_default(self):
        """Test default value for missing nested keys."""
        config = CompatConfigLoader()
        result = config.get("paths", "nonexistent", default="default")
        assert result == "default"

    def test_paths_property(self):
        """Test paths property returns dict."""
        config = CompatConfigLoader()
        assert isinstance(config.paths, dict)

    def test_game_constants_property(self):
        """Test game_constants property returns dict."""
        config = CompatConfigLoader()
        assert isinstance(config.game_constants, dict)

    def test_variants_property(self):
        """Test variants property returns dict."""
        config = CompatConfigLoader()
        assert isinstance(config.variants, dict)


class TestGlobalConfigAccess:
    """Test cases for global config access functions."""

    def test_get_config_singleton(self):
        """Test that get_config returns the same instance."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_config_properties_work(self):
        """Test that config properties return expected types."""
        config = get_config()
        assert isinstance(config.paths, dict)
        assert isinstance(config.game_constants, dict)
        assert isinstance(config.messages, dict)
