from pathlib import Path

import pytest
import typer

from src.kachi.backup import backup_dir, backup_file, backup_profile
from src.kachi.config import Profile


class TestBackupFunctions:
    def test_backup_file(self, tmp_path: Path):
        """Test that the file is successfully copied to the destination folder"""
        d = tmp_path / "test-dir"
        d.mkdir()
        f = d / "test-file.txt"
        content = "I am a test backup file"
        f.write_text(content)

        backup_file(f, tmp_path)
        assert (tmp_path / f.name).exists()
        assert (tmp_path / f.name).read_text() == content

    def test_backup_dir(self, tmp_path: Path):
        """Test that the directory is successfully copied to the destination folder"""
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
        """Test that the profile is successfully backed up"""
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
                backup_destination=str(backupdir),
            )
        )

        assert (backupdir / tmp1.name).exists()
        assert (backupdir / "test-dir" / tmp2.name).exists()

    def test_backup_profile_has_invaild_backup_destination(self, tmp_path: Path):
        """Test that an invalid backup destination raises an error"""
        profile = Profile(
            name="test_profile",
            sources=[tmp_path / "test-file.txt"],
            backup_destination=tmp_path / "invalid-dir",
        )

        with pytest.raises(Exception):
            backup_profile(profile, tmp_path)

    def test_invalid_source_in_profile(self, tmp_path: Path):
        """Test that an invalid profile name raises an error"""
        data = {
            "name": "default",
            "sources": [tmp_path / "test-file.txt"],
            "backup_destination": tmp_path,
        }

        profile = Profile(**data)
        nf = backup_profile(profile)
        assert nf == [tmp_path / "test-file.txt"]

    def test_backup_file_exception(self, tmp_path: Path):
        """Test that an exception is raised when the file cannot be backed up"""
        f = tmp_path / "test-file.txt"
        f.touch()
        f.chmod(0o000)

        with pytest.raises(Exception):
            backup_file(f, tmp_path / "backup-dir")

    def test_backup_dir_not_exist_and_exits(self, tmp_path: Path):
        """Test that an exception is raised when the directory does not exist"""
        d = tmp_path / "test-dir"

        with pytest.raises(Exception):
            backup_dir(d, tmp_path / "backup-dir")

        assert typer.Exit(code=1)
