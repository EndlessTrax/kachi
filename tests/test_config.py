import pytest
from kachi.config import Config, Settings, Profile, DEFAULT_CONFIG_PATH

@pytest.fixture
def test_config_path():
    return "examples/example.yaml"


def test_sets_default_config_path():
    config = Config()
    assert config.filepath == DEFAULT_CONFIG_PATH

def test_sets_custom_config_path(test_config_path):
    config = Config(test_config_path)
    assert config.filepath == test_config_path

def test_profile_dataclass():
    profile = Profile(
        name = "test_profile",
        sources = [".bashrc", ".gitconfig"],
        backup_dest = "/home/user/backup"
    )
    assert profile.name == "test_profile"
    assert profile.sources == [".bashrc", ".gitconfig"]
    assert profile.backup_dest == "/home/user/backup"

def test_settings_class(test_config_path):
    settings = Settings(test_config_path)
    assert len(settings.settings) == 3
    assert settings.settings[0].name == "default"
    assert settings.settings[0].sources == [".gitconfig"]
    assert settings.settings[2].name == "linux"
    assert settings.settings[2].sources == [".bashrc", ".gitconfig"]
    assert settings.settings[2].backup_dest == "/home/user/backup"

