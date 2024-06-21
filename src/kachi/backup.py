import pathlib
import shutil

import typer

from kachi import logger
from kachi.config import Profile


def backup_dir(src: pathlib.Path, dest: pathlib.Path) -> None:
    """Copy a directory from src to dest."""
    try:
        dest_dir_name = dest / src.name
        if not pathlib.Path(dest_dir_name).exists():
            dest_dir_name.mkdir(exist_ok=True)

        shutil.copytree(src, dest_dir_name, dirs_exist_ok=True)
        logger.info(
            f"Backed up directory, all subdirectories, and files for {str(src)} to {str(dest)}"  # noqa: E501
        )
    except shutil.Error as e:
        logger.error(f"Unable to backup {str(src)}")
        logger.exception(e)


def backup_file(src: pathlib.Path, dest: pathlib.Path) -> None:
    """Copy a file from src to dest."""
    try:
        f = pathlib.Path(src).name
        shutil.copy2(src, (dest / f))
        logger.info(f"Backed up {str(src)} to {str(dest)}")
    except shutil.Error as e:
        logger.error(f"Unable to backup {str(src)}")
        logger.exception(e)


def backup_profile(profile: Profile) -> list:
    """Backup a profile."""
    
    backup_dir = pathlib.Path(profile.backup_destination)
    if not backup_dir.exists() or not backup_dir.is_dir():
        logger.error(f"Destination is not a directory: {profile.backup_destination}")
        raise typer.Exit(code=1)

    logger.info(f"Backing up profile: {profile}")

    sources_not_found = []
    for source in profile.sources:
        src = pathlib.Path(source)
        if pathlib.Path(src).is_file():
            backup_file(src, backup_dir)
        elif pathlib.Path(src).is_dir():
            backup_dir(src, backup_dir)
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
