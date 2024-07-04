import shutil
from pathlib import Path

import typer

from kachi import logger
from kachi.config import Profile


def backup_dir(src: Path, dest: Path) -> None:
    """Copy a directory from src to dest."""
    try:
        dest_dir_name = dest / src.name
        if not Path(dest_dir_name).exists():
            dest_dir_name.mkdir(exist_ok=True)

        shutil.copytree(src, dest_dir_name, dirs_exist_ok=True)
        logger.info(
            f"Backed up directory, all subdirectories, and files for {str(src)} to {str(dest)}"  # noqa: E501
        )
    except shutil.Error as e:
        logger.error(f"Unable to backup {str(src)}")
        logger.exception(e)


def backup_file(src: Path, dest: Path) -> None:
    """Copy a file from src to dest."""
    try:
        f = Path(src).name
        shutil.copy2(src, (dest / f))
        logger.info(f"Backed up {str(src)} to {str(dest)}")
    except shutil.Error as e:
        logger.error(f"Unable to backup {str(src)}")
        logger.exception(e)


def backup_profile(profile: Profile) -> list:
    """Backup a profile."""
    dest = Path(profile.backup_destination)
    if not dest.exists() or not dest.is_dir():
        logger.error(f"Destination is not a directory: {profile.backup_destination}")
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
            logger.error(f"{str(src)} not found")

    return sources_not_found


def log_not_found(not_found: list) -> None:
    """Log sources not found at the end of the backup."""
    if len(not_found) > 0:
        logger.warning(f"{len(not_found)} sources not backed up.")

        for nf in not_found:
            logger.warning(f"Source not found: {str(nf)}")
