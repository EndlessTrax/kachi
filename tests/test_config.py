"""Tests for the configuration parsing module."""

from pathlib import Path

import pytest

from src.kachi.config import DEFAULT_CONFIG_PATH, Config, Profile, Settings


@pytest.fixture
def test_config_path() -> Path:
    """Return the path to the example configuration file."""
    return Path("examples/example.yaml")


class TestConfig:
    """Tests for Config, Settings, and Profile classes."""

    def test_sets_default_config_path(self):
        """Test that Config uses the default path when none is provided."""
        config = Config()
        assert config.filepath == DEFAULT_CONFIG_PATH

    def test_sets_custom_config_path(self, test_config_path: Path):
        """Test that Config uses a custom path when provided."""
        config = Config(test_config_path)
        assert config.filepath == test_config_path

    def test_invalid_config_path(self):
        """Test that a nonexistent config path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            Config(Path("invalid/path.yaml"))

    def test_profile_dataclass(self):
        """Test that the Profile dataclass stores fields correctly."""
        profile = Profile(
            name="test_profile",
            sources=[Path(".bashrc"), Path(".gitconfig")],
            backup_destination=Path("/home/user/backup"),
        )
        assert profile.name == "test_profile"
        assert profile.sources == [Path(".bashrc"), Path(".gitconfig")]
        assert profile.backup_destination == Path("/home/user/backup")

    def test_settings_class(self, test_config_path: Path):
        """Test that Settings parses profiles with default inheritance."""
        settings = Settings(test_config_path)
        assert len(settings.settings) == 3
        assert settings.settings[0].name == "default"
        assert settings.settings[0].sources == [Path(".gitconfig")]
        assert settings.settings[2].name == "linux"
        assert settings.settings[2].sources == [Path(".bashrc"), Path(".gitconfig")]
        assert settings.settings[2].backup_destination == Path("/home/user/backup")

    def test_config_parse_function(self, test_config_path: Path):
        """Test that Config.parse populates settings from the config file."""
        config = Config(test_config_path)
        config.parse()
        assert len(config.settings) == 3
        assert config.settings[0].name == "default"
        assert config.settings[0].sources == [Path(".gitconfig")]

    def test_config_get_profile_function(self, test_config_path: Path):
        """Test that get_profile returns the correct profile by name."""
        config = Config(test_config_path)
        config.parse()
        profile = config.get_profile("linux")
        assert profile.name == "linux"
        assert profile.sources == [Path(".bashrc"), Path(".gitconfig")]
        assert profile.backup_destination == Path("/home/user/backup")

    def test_config_get_profile_function_invalid_profile_name(
        self, test_config_path: Path
    ):
        """Test that get_profile raises ValueError for an unknown name."""
        config = Config(test_config_path)
        config.parse()
        with pytest.raises(ValueError):
            config.get_profile("invalid_profile")
