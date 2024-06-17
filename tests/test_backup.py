from src.kachi.backup import backup_dir, backup_file, backup_profile
from src.kachi.config import Profile


class TestBackupFunctions:
    def test_backup_file(self, tmp_path):
        """Test that the file is successfully copied to the destination folder"""
        d = tmp_path / "test-dir"
        d.mkdir()
        f = d / "test-file.txt"
        content = "I am a test backup file"
        f.write_text(content)

        backup_file(f, tmp_path)
        assert (tmp_path / f.name).exists()
        assert (tmp_path / f.name).read_text() == content

    def test_backup_dir(self, tmp_path):
        """Test that the directory is successfully copied to the destination folder"""
        d1 = tmp_path / "test-dir"
        d2 = tmp_path / "test-dir-backup"
        d1.mkdir()
        d2.mkdir()

        f = d1 / "test-file.txt"
        content = "I am a test backup file for a directory"
        f.write_text(content)

        backup_dir(d1, d2)
        assert (d2 / f.name).exists()

    def test_backup_profile(self, tmp_path):
        """Test that the profile is successfully backed up"""
        tmp1 = tmp_path / "test-file-1.txt"
        tmpdir = tmp_path / "test-dir"
        backupdir = tmp_path / "backup-dir"
        tmpdir.mkdir()
        backupdir.mkdir()

        content = "Testing profile backup"
        tmp1.write_text(content)
        tmp2 = tmpdir / "test-file-2.txt"
        tmp2.write_text(content)

        profile = Profile(
            name="test_profile", sources=[tmp1, tmpdir], backup_dest=backup_dir
        )

        backup_profile(profile, backupdir)

        assert (backupdir / tmp1.name).exists()
        assert (backupdir / tmp2.name).exists()
