import shutil
from pathlib import Path

import typer

from kachi import logger
from kachi.config import Profile
from kachi.errors import BackupErrorHandler

# Create a module-level error handler to avoid unnecessary object creation
error_handler = BackupErrorHandler(logger)


def backup_dir(src: Path, dest: Path) -> bool:
    """Copy a directory from src to dest.

    Returns:
        True if the backup was successful, False if an error occurred.
    """
    try:
        dest_dir_name = dest / src.name
        if not Path(dest_dir_name).exists():
            dest_dir_name.mkdir(exist_ok=True)

        shutil.copytree(src, dest_dir_name, dirs_exist_ok=True)
        logger.info(
            f"Backed up directory, all subdirectories, and files for {str(src)} to {str(dest)}"  # noqa: E501
        )
        return True
    except PermissionError:
        error_handler.handle_permission_error(src)
        return False
    except FileNotFoundError:
        # Let FileNotFoundError propagate for proper error handling
        raise
    except shutil.Error as e:
        error_handler.handle_shutil_error(e, src)
        return False
    except OSError as e:
        # Catch any remaining OS-level errors (e.g., permission errors not caught above)
        if e.errno == 13:  # Permission denied
            error_handler.handle_permission_error(src)
        else:
            error_handler.handle_shutil_error(e, src)
        return False


def backup_file(src: Path, dest: Path) -> bool:
    """Copy a file from src to dest.

    Returns:
        True if the backup was successful, False if an error occurred.
    """
    try:
        f = Path(src).name
        shutil.copy2(src, (dest / f))
        logger.info(f"Backed up {str(src)} to {str(dest)}")
        return True
    except PermissionError:
        error_handler.handle_permission_error(src)
        return False
    except FileNotFoundError:
        # Let FileNotFoundError propagate for proper error handling
        raise
    except shutil.Error as e:
        error_handler.handle_shutil_error(e, src)
        return False
    except OSError as e:
        # Catch any remaining OS-level errors (e.g., permission errors not caught above)
        if e.errno == 13:  # Permission denied
            error_handler.handle_permission_error(src)
        else:
            error_handler.handle_shutil_error(e, src)
        return False


def backup_profile(profile: Profile) -> tuple[list, int, int]:
    """Backup a profile.

    Returns:
        A tuple containing:
        - List of sources not found
        - Count of successfully backed up sources
        - Count of errors encountered
    """
    dest = profile.backup_destination
    if not dest.exists() or not dest.is_dir():
        error_handler.handle_invalid_destination(dest)
        raise typer.Exit(code=1)

    logger.info(f"Backing up profile: {profile}")

    sources_not_found = []
    success_count = 0
    error_count = 0

    for src in profile.sources:
        if src.is_file():
            if backup_file(src, dest):
                success_count += 1
            else:
                error_count += 1
        elif src.is_dir():
            if backup_dir(src, dest):
                success_count += 1
            else:
                error_count += 1
        else:
            sources_not_found.append(src)
            error_handler.handle_file_not_found(src)
            error_count += 1

    return sources_not_found, success_count, error_count


def log_not_found(not_found: list) -> None:
    """Log sources not found at the end of the backup."""
    if len(not_found) > 0:
        logger.warning(f"{len(not_found)} sources not backed up.")

        for nf in not_found:
            logger.warning(f"Source not found: {str(nf)}")
