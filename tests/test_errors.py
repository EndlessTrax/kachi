"""Tests for error handling module."""

from pathlib import Path
from unittest.mock import Mock

from src.kachi.errors import BackupErrorHandler


class TestBackupErrorHandler:
    """Tests for BackupErrorHandler class."""

    def test_handle_permission_error(self):
        """Test that permission errors are handled correctly."""
        mock_logger = Mock()
        error_handler = BackupErrorHandler(mock_logger)
        test_path = Path("/test/path/file.txt")

        error_handler.handle_permission_error(test_path)

        # Verify error message was logged
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Permission denied" in error_call
        assert str(test_path) in error_call

        # Verify warning message was logged
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Skipping" in warning_call
        assert str(test_path) in warning_call

    def test_handle_shutil_error(self):
        """Test that shutil errors are handled correctly."""
        mock_logger = Mock()
        error_handler = BackupErrorHandler(mock_logger)
        test_path = Path("/test/path/file.txt")
        test_error = Exception("Some shutil error")

        error_handler.handle_shutil_error(test_error, test_path)

        # Verify both error messages were logged
        assert mock_logger.error.call_count == 2
        first_call = mock_logger.error.call_args_list[0][0][0]
        second_call = mock_logger.error.call_args_list[1][0][0]

        assert "Unable to backup" in first_call
        assert str(test_path) in first_call
        assert "Error details" in second_call

    def test_handle_file_not_found(self):
        """Test that file not found errors are handled correctly."""
        mock_logger = Mock()
        error_handler = BackupErrorHandler(mock_logger)
        test_path = Path("/test/path/missing.txt")

        error_handler.handle_file_not_found(test_path)

        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert str(test_path) in error_call
        assert "not found" in error_call

    def test_handle_invalid_destination(self):
        """Test that invalid destination errors are handled correctly."""
        mock_logger = Mock()
        error_handler = BackupErrorHandler(mock_logger)
        test_path = Path("/test/invalid/destination")

        error_handler.handle_invalid_destination(test_path)

        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Destination is not a directory" in error_call
        assert str(test_path) in error_call
