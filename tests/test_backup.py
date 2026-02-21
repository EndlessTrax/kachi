"""Tests for the backup module."""

from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from src.kachi.backup import backup_dir, backup_file, backup_profile, log_not_found
from src.kachi.config import Profile


class TestBackupFunctions:
    """Tests for backup_file, backup_dir, backup_profile, and log_not_found."""

    def test_backup_file(self, tmp_path: Path):
        """Test that the file is successfully copied to the destination folder."""
        d = tmp_path / "test-dir"
        d.mkdir()
        f = d / "test-file.txt"
        content = "I am a test backup file"
        f.write_text(content)

        backup_file(f, tmp_path)
        assert (tmp_path / f.name).exists()
        assert (tmp_path / f.name).read_text() == content

    def test_backup_dir(self, tmp_path: Path):
        """Test that the directory is successfully copied to the destination folder."""
        d = tmp_path / "test-dir"
        d.mkdir()
        f = d / "test-file.txt"
        content = "I am a test backup file"
        f.write_text(content)

        backup_dir(d, tmp_path)
        assert (tmp_path / d.name).exists()
        assert (tmp_path / d.name / f.name).exists()
        assert (tmp_path / d.name / f.name).read_text() == content

    def test_backup_profile(self, tmp_path: Path):
        """Test that the profile is successfully backed up."""
        tmpdir = tmp_path / "test-dir"
        backupdir = tmp_path / "backup-dir"
        tmpdir.mkdir()
        backupdir.mkdir()

        content = "Testing profile backup"
        tmp1 = tmp_path / "test-file-1.txt"
        tmp1.write_text(content)
        tmp2 = tmpdir / "test-file-2.txt"
        tmp2.write_text(content)

        _ = backup_profile(
            Profile(
                name="test_profile",
                sources=[tmp1, tmpdir],
                backup_destination=backupdir,
            )
        )

        assert (backupdir / tmp1.name).exists()
        assert (backupdir / "test-dir" / tmp2.name).exists()

    def test_backup_profile_has_invaild_backup_destination(self, tmp_path: Path):
        """Test that an invalid backup destination raises an error."""
        profile = Profile(
            name="test_profile",
            sources=[tmp_path / "test-file.txt"],
            backup_destination=tmp_path / "invalid-dir",
        )

        with pytest.raises(Exception):
            backup_profile(profile)

    def test_invalid_source_in_profile(self, tmp_path: Path):
        """Test that an invalid profile name raises an error."""
        data = {
            "name": "default",
            "sources": [tmp_path / "test-file.txt"],
            "backup_destination": tmp_path,
        }

        profile = Profile(**data)
        nf, success_count, error_count = backup_profile(profile)
        assert nf == [tmp_path / "test-file.txt"]
        assert success_count == 0
        assert error_count == 1

    def test_backup_file_permission_error(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ):
        """Test that permission errors are logged correctly when backing up a file."""
        dest = tmp_path / "backup-dir"
        dest.mkdir()
        f = tmp_path / "test-file.txt"
        f.write_text("test content")

        with patch("shutil.copy2", side_effect=PermissionError("Permission denied")):
            # Permission error should be caught and logged, not raised
            backup_file(f, dest)

            # Verify error message was logged
            assert "Permission denied" in caplog.text
            assert str(f) in caplog.text
            assert "Skipping" in caplog.text

            # Verify the backup operation failed (file not copied)
            assert not (dest / f.name).exists()

    def test_backup_dir_permission_error(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ):
        """Test permission errors are logged correctly when backing up a directory."""
        dest = tmp_path / "backup-dir"
        dest.mkdir()
        test_dir = tmp_path / "test-dir"
        test_dir.mkdir()
        test_file = test_dir / "test-file.txt"
        test_file.write_text("test content")

        with patch(
            "shutil.copytree", side_effect=PermissionError("Permission denied")
        ):
            # Permission error should be caught and logged, not raised
            backup_dir(test_dir, dest)

            # Verify error message was logged
            assert "Permission denied" in caplog.text
            assert str(test_dir) in caplog.text

    def test_backup_dir_not_exist_and_exits(self, tmp_path: Path):
        """Test that an exception is raised when the directory does not exist."""
        d = tmp_path / "test-dir"

        with pytest.raises(Exception):
            backup_dir(d, tmp_path / "backup-dir")

        assert typer.Exit(code=1)

    def test_log_not_found_func(self, caplog: pytest.LogCaptureFixture):
        """Test that the sources not found are logged."""
        not_found = [Path("test-file-1.txt"), Path("test-file-2.txt")]
        log_not_found(not_found)

        assert "2 sources not backed up." in caplog.text
        assert "Source not found: test-file-1.txt" in caplog.text
        assert "Source not found: test-file-2.txt" in caplog.text

    def test_backup_file_returns_true_on_success(self, tmp_path: Path):
        """Test that backup_file returns True on success."""
        d = tmp_path / "test-dir"
        d.mkdir()
        f = d / "test-file.txt"
        f.write_text("test content")

        result = backup_file(f, tmp_path)
        assert result is True

    def test_backup_file_returns_false_on_permission_error(self, tmp_path: Path):
        """Test that backup_file returns False on permission error."""
        backup_dest = tmp_path / "backup-dir"
        backup_dest.mkdir()
        f = tmp_path / "test-file.txt"
        f.write_text("test content")

        with patch("shutil.copy2", side_effect=PermissionError("Permission denied")):
            result = backup_file(f, backup_dest)
            assert result is False

    def test_backup_dir_returns_true_on_success(self, tmp_path: Path):
        """Test that backup_dir returns True on success."""
        src_dir = tmp_path / "source-dir"
        dest_dir = tmp_path / "dest-dir"
        src_dir.mkdir()
        dest_dir.mkdir()
        f = src_dir / "test-file.txt"
        f.write_text("test content")

        result = backup_dir(src_dir, dest_dir)
        assert result is True

    def test_backup_dir_returns_false_on_permission_error(self, tmp_path: Path):
        """Test that backup_dir returns False on permission error."""
        dest = tmp_path / "backup-dir"
        dest.mkdir()
        test_dir = tmp_path / "test-dir"
        test_dir.mkdir()
        test_file = test_dir / "test-file.txt"
        test_file.write_text("test content")

        with patch(
            "shutil.copytree", side_effect=PermissionError("Permission denied")
        ):
            result = backup_dir(test_dir, dest)
            assert result is False

    def test_backup_profile_returns_counts(self, tmp_path: Path):
        """Test that backup_profile returns success and error counts."""
        tmpdir = tmp_path / "test-dir"
        backupdir = tmp_path / "backup-dir"
        tmpdir.mkdir()
        backupdir.mkdir()

        tmp1 = tmp_path / "test-file-1.txt"
        tmp1.write_text("test content")
        tmp2 = tmpdir / "test-file-2.txt"
        tmp2.write_text("test content")

        nf, success_count, error_count = backup_profile(
            Profile(
                name="test_profile",
                sources=[tmp1, tmpdir],
                backup_destination=backupdir,
            )
        )

        assert nf == []
        assert success_count == 2
        assert error_count == 0

    def test_backup_profile_counts_mixed_sources(self, tmp_path: Path):
        """Test that backup_profile counts both successes and errors correctly."""
        backupdir = tmp_path / "backup-dir"
        backupdir.mkdir()

        existing_file = tmp_path / "existing-file.txt"
        existing_file.write_text("test content")

        nf, success_count, error_count = backup_profile(
            Profile(
                name="test_profile",
                sources=[existing_file, tmp_path / "nonexistent.txt"],
                backup_destination=backupdir,
            )
        )

        assert len(nf) == 1
        assert success_count == 1
        assert error_count == 1
