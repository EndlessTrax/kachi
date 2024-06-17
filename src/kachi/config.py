import pathlib
from dataclasses import dataclass

import yaml
from kachi import logger

DEFAULT_CONFIG_PATH = pathlib.Path.home() / ".config" / "kachi" / "config.yaml"


@dataclass
class Profile:
    name: str
    sources: list[str]
    backup_destination: str


class Settings:
    def __init__(self, filepath):
        self.settings = self._parse_settings(filepath)

    def _parse_settings(self, filepath):
        with open(filepath, "r", encoding="utf8") as f:
            self.raw_content = f.read()

        parsed_contents = yaml.safe_load(self.raw_content)

        settings = []
        default_sources = []
        default_backup_dest = None

        if "default" in parsed_contents["profiles"]:
            if "sources" in parsed_contents["profiles"]["default"]:
                default_sources.extend(
                    parsed_contents["profiles"]["default"]["sources"]
                )
            if "backup_destination" in parsed_contents["profiles"]["default"]:
                default_backup_dest = parsed_contents["profiles"]["default"][
                    "backup_destination"
                ]

            settings.append(
                Profile(
                    name="default",
                    sources=default_sources,
                    backup_destination=default_backup_dest,
                )
            )

        for k, v in parsed_contents["profiles"].items():
            if k != "default":
                settings.append(
                    Profile(
                        name=k,
                        sources=[*v["sources"], *default_sources]
                        if "sources" in v
                        else default_sources,
                        backup_destination=v["backup_destination"]
                        if "backup_destination" in v
                        else default_backup_dest,
                    )
                )

        return settings


class Config:
    def __init__(self, filepath=None):
        self.filepath = self._set_filepath(filepath)

    def _set_filepath(self, filepath: str):
        if filepath == "" or filepath is None:
            logger.info(f"Using default config path: {DEFAULT_CONFIG_PATH}")
            return DEFAULT_CONFIG_PATH

        if not pathlib.Path(filepath).exists():
            raise FileNotFoundError(logger.error(f"Config file not found: {filepath}"))

        logger.info(f"Using config path: {filepath}")
        return filepath

    def parse(self):
        self.settings = Settings(self.filepath).settings

    def get_profile(self, name: str):
        for profile in self.settings:
            if profile.name == name:
                return profile
        return None  # TODO: Raise an exception here
