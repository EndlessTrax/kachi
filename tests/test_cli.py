"""Tests for the CLI module."""

import logging
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from kachi import __version__
from kachi.cli import app

runner = CliRunner()


class TestCli:
    """Tests for Kachi CLI commands and flags."""

    def test_get_version(self):
        """Test that --version prints the current version and exits cleanly."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "kachi" in result.stdout
        assert __version__ in result.stdout

    def test_backup_command_runs_successfully(self):
        """Test that backup command runs successfully with new logging format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")

            backup_dir = Path(tmpdir) / "backup"
            backup_dir.mkdir()

            # Create config
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text(
                f"profiles:\n"
                f"  default:\n"
                f"    sources:\n"
                f"      - {test_file}\n"
                f"    backup_destination: {backup_dir}\n"
            )

            # Run backup - should succeed with new logging format
            result = runner.invoke(app, ["backup", "--config", str(config_file)])
            assert result.exit_code == 0

            # Verify backup was successful by checking file exists
            backed_up_file = backup_dir / "test.txt"
            assert backed_up_file.exists()
            assert backed_up_file.read_text() == "test content"

    def _make_empty_config(self, tmpdir: str) -> Path:
        """Create a minimal config file with no sources for verbosity tests.

        Args:
            tmpdir: Path to the temporary directory.

        Returns:
            Path to the created config file.
        """
        backup_dir = Path(tmpdir) / "backup"
        backup_dir.mkdir()
        config_file = Path(tmpdir) / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  default:\n"
            "    sources: []\n"
            f"    backup_destination: {backup_dir}\n"
        )
        return config_file

    def test_quiet_flag_sets_warning_level(self):
        """Test that --quiet sets the root logger level to WARNING."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = self._make_empty_config(tmpdir)
            result = runner.invoke(
                app, ["--quiet", "backup", "--config", str(config_file)]
            )
            assert result.exit_code == 0
            assert logging.getLogger().level == logging.WARNING

    def test_quiet_short_flag_sets_warning_level(self):
        """Test that -q sets the root logger level to WARNING."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = self._make_empty_config(tmpdir)
            result = runner.invoke(app, ["-q", "backup", "--config", str(config_file)])
            assert result.exit_code == 0
            assert logging.getLogger().level == logging.WARNING

    def test_verbose_flag_sets_debug_level(self):
        """Test that --verbose sets the root logger level to DEBUG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = self._make_empty_config(tmpdir)
            result = runner.invoke(
                app, ["--verbose", "backup", "--config", str(config_file)]
            )
            assert result.exit_code == 0
            assert logging.getLogger().level == logging.DEBUG

    def test_verbose_short_flag_sets_debug_level(self):
        """Test that -v sets the root logger level to DEBUG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = self._make_empty_config(tmpdir)
            result = runner.invoke(app, ["-v", "backup", "--config", str(config_file)])
            assert result.exit_code == 0
            assert logging.getLogger().level == logging.DEBUG

    def test_quiet_and_verbose_together_exits_with_error(self):
        """Test that combining --quiet and --verbose exits with an error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = self._make_empty_config(tmpdir)
            result = runner.invoke(
                app, ["--quiet", "--verbose", "backup", "--config", str(config_file)]
            )
            assert result.exit_code == 1
