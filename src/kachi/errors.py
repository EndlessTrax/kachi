"""Error handling module for Kachi backup operations."""

from pathlib import Path
from typing import Protocol


class ErrorLogger(Protocol):
    """Protocol for logging errors."""

    def error(self, message: str) -> None:
        """Log an error message."""
        ...

    def warning(self, message: str) -> None:
        """Log a warning message."""
        ...


class BackupErrorHandler:
    """Handler for backup operation errors using composition."""

    def __init__(self, logger: ErrorLogger):
        """
        Initialize the error handler.

        Args:
            logger: A logger instance that implements the ErrorLogger protocol.
        """
        self.logger = logger

    def handle_permission_error(self, _error: PermissionError, source: Path) -> None:
        """
        Handle permission errors during backup operations.

        Args:
            _error: The PermissionError that occurred (currently unused).
            source: The source path that caused the error.
        """
        self.logger.error(
            f"Permission denied while accessing {str(source)}. "
            "Please check file/folder permissions."
        )
        self.logger.warning(f"Skipping {str(source)} due to permission error.")

    def handle_shutil_error(self, error: Exception, source: Path) -> None:
        """
        Handle shutil errors during backup operations.

        Args:
            error: The shutil error that occurred.
            source: The source path that caused the error.
        """
        self.logger.error(f"Unable to backup {str(source)}")
        # Log the exception for debugging purposes
        self.logger.error(f"Error details: {str(error)}")

    def handle_file_not_found(self, source: Path) -> None:
        """
        Handle file not found errors.

        Args:
            source: The source path that was not found.
        """
        self.logger.error(f"{str(source)} not found")

    def handle_invalid_destination(self, destination: Path) -> None:
        """
        Handle invalid destination errors.

        Args:
            destination: The invalid destination path.
        """
        self.logger.error(f"Destination is not a directory: {str(destination)}")
