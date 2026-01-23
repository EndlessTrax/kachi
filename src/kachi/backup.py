import shutil
from pathlib import Path

import typer

from kachi import logger
from kachi.config import Profile
from kachi.errors import BackupErrorHandler


def backup_dir(src: Path, dest: Path) -> None:
    """Copy a directory from src to dest."""
    error_handler = BackupErrorHandler(logger)
    try:
        dest_dir_name = dest / src.name
        if not Path(dest_dir_name).exists():
            dest_dir_name.mkdir(exist_ok=True)

        shutil.copytree(src, dest_dir_name, dirs_exist_ok=True)
        logger.info(
            f"Backed up directory, all subdirectories, and files for {str(src)} to {str(dest)}"  # noqa: E501
        )
    except PermissionError as e:
        error_handler.handle_permission_error(e, src)
    except shutil.Error as e:
        error_handler.handle_shutil_error(e, src)


def backup_file(src: Path, dest: Path) -> None:
    """Copy a file from src to dest."""
    error_handler = BackupErrorHandler(logger)
    try:
        f = Path(src).name
        shutil.copy2(src, (dest / f))
        logger.info(f"Backed up {str(src)} to {str(dest)}")
    except PermissionError as e:
        error_handler.handle_permission_error(e, src)
    except shutil.Error as e:
        error_handler.handle_shutil_error(e, src)


def backup_profile(profile: Profile) -> list:
    """Backup a profile."""
    error_handler = BackupErrorHandler(logger)
    dest = Path(profile.backup_destination)
    if not dest.exists() or not dest.is_dir():
        error_handler.handle_invalid_destination(dest)
        raise typer.Exit(code=1)

    logger.info(f"Backing up profile: {profile}")

    sources_not_found = []
    for source in profile.sources:
        src = Path(source)
        if Path(src).is_file():
            backup_file(src, dest)
        elif Path(src).is_dir():
            backup_dir(src, dest)
        else:
            sources_not_found.append(src)
            error_handler.handle_file_not_found(src)

    return sources_not_found


def log_not_found(not_found: list) -> None:
    """Log sources not found at the end of the backup."""
    if len(not_found) > 0:
        logger.warning(f"{len(not_found)} sources not backed up.")

        for nf in not_found:
            logger.warning(f"Source not found: {str(nf)}")
