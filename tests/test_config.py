import pytest

from src.kachi.config import DEFAULT_CONFIG_PATH, Config, Profile, Settings


@pytest.fixture
def test_config_path():
    return "examples/example.yaml"


class TestConfig:
    def test_sets_default_config_path(self):
        config = Config()
        assert config.filepath == DEFAULT_CONFIG_PATH

    def test_sets_custom_config_path(self, test_config_path):
        config = Config(test_config_path)
        assert config.filepath == test_config_path

    def test_invalid_config_path(self):
        with pytest.raises(FileNotFoundError):
            Config("invalid/path.yaml")

    def test_profile_dataclass(self):
        profile = Profile(
            name="test_profile",
            sources=[".bashrc", ".gitconfig"],
            backup_destination="/home/user/backup",
        )
        assert profile.name == "test_profile"
        assert profile.sources == [".bashrc", ".gitconfig"]
        assert profile.backup_destination == "/home/user/backup"

    def test_settings_class(self, test_config_path):
        settings = Settings(test_config_path)
        assert len(settings.settings) == 3
        assert settings.settings[0].name == "default"
        assert settings.settings[0].sources == [".gitconfig"]
        assert settings.settings[2].name == "linux"
        assert settings.settings[2].sources == [".bashrc", ".gitconfig"]
        assert settings.settings[2].backup_destination == "/home/user/backup"

    def test_config_parse_function(self, test_config_path):
        config = Config(test_config_path)
        config.parse()
        assert len(config.settings) == 3
        assert config.settings[0].name == "default"
        assert config.settings[0].sources == [".gitconfig"]

    def test_config_get_profile_function(self, test_config_path):
        config = Config(test_config_path)
        config.parse()
        profile = config.get_profile("linux")
        assert profile.name == "linux"
        assert profile.sources == [".bashrc", ".gitconfig"]
        assert profile.backup_destination == "/home/user/backup"
    
    def test_config_get_profile_function_invalid_profile_name(self, test_config_path):
        config = Config(test_config_path)
        config.parse()
        with pytest.raises(ValueError):
            config.get_profile("invalid_profile")
