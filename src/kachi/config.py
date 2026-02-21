"""YAML configuration parsing for Kachi backup profiles."""

import pathlib
from dataclasses import dataclass
from pathlib import Path

import yaml

from kachi import logger

DEFAULT_CONFIG_PATH = pathlib.Path.home() / ".config" / "kachi" / "config.yaml"


@dataclass
class Profile:
    """A backup profile parsed from the configuration file.

    Attributes:
        name: The profile name as defined in the YAML config.
        sources: Paths to files or directories to back up.
        backup_destination: Directory where backups are stored,
            or ``None`` if unset.
    """

    name: str
    sources: list[Path]
    backup_destination: Path | None


class Settings:
    """Parse a YAML configuration file into a list of profiles."""

    def __init__(self, filepath):
        """Initialize Settings by parsing the given configuration file.

        Args:
            filepath: Path to the YAML configuration file.
        """
        self.settings = self._parse_settings(filepath)

    def _parse_settings(self, filepath) -> list[Profile]:
        """Parse YAML content into a list of Profile objects.

        Applies default-profile inheritance: the default profile's sources
        are appended to every other profile, and its ``backup_destination``
        is used as a fallback when a profile does not declare one.

        Args:
            filepath: Path to the YAML configuration file.

        Returns:
            A list of parsed Profile objects.
        """
        with open(filepath, "r", encoding="utf8") as f:
            self.raw_content = f.read()

        parsed_contents = yaml.safe_load(self.raw_content)

        settings = []
        default_sources = []
        default_backup_dest = None

        # Apply default-profile inheritance: append its sources to every
        # other profile and use its backup_destination as a fallback.
        if "default" in parsed_contents["profiles"]:
            if "sources" in parsed_contents["profiles"]["default"]:
                default_sources.extend(
                    Path(s)
                    for s in parsed_contents["profiles"]["default"]["sources"]
                )
            if "backup_destination" in parsed_contents["profiles"]["default"]:
                default_backup_dest = Path(
                    parsed_contents["profiles"]["default"]["backup_destination"]
                )

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
                        sources=[*[Path(s) for s in v["sources"]], *default_sources]
                        if "sources" in v
                        else list(default_sources),
                        backup_destination=Path(v["backup_destination"])
                        if "backup_destination" in v
                        else default_backup_dest,
                    )
                )

        return settings


class Config:
    """Manage the Kachi configuration file location and parsed profiles."""

    def __init__(self, filepath: Path | None = None):
        """Initialize Config with an optional custom file path.

        Args:
            filepath: Path to the configuration file. Falls back to
                ``DEFAULT_CONFIG_PATH`` when ``None``.
        """
        self.filepath = self._set_filepath(filepath)

    def _set_filepath(self, filepath: Path | None) -> Path:
        """Resolve and validate the configuration file path.

        Args:
            filepath: An explicit path, or ``None`` to use the default.

        Returns:
            The resolved configuration file Path.

        Raises:
            FileNotFoundError: If the given path does not exist or is not a file.
        """
        if filepath is None:
            logger.info(f"Using default config path: {DEFAULT_CONFIG_PATH}")
            return DEFAULT_CONFIG_PATH

        path = pathlib.Path(filepath)
        if not path.is_file():
            msg = f"Config file not found: {filepath}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        logger.info(f"Using config path: {filepath}")
        return path

    def parse(self) -> None:
        """Parse the configuration file and populate ``self.settings``."""
        self.settings = Settings(self.filepath).settings

    def get_profile(self, name: str) -> Profile:
        """Retrieve a profile by name.

        Args:
            name: The profile name to look up.

        Returns:
            The matching Profile object.

        Raises:
            ValueError: If no profile with the given name exists.
        """
        for profile in self.settings:
            if profile.name == name:
                return profile
        else:
            raise ValueError(f"Profile with name '{name}' not found.")
