import pathlib
import shutil

from kachi.config import Profile
from kachi import logger


def backup_dir(src: pathlib.Path, dest: pathlib.Path) -> None:
    """Copy a directory from src to dest."""
    try:
        shutil.copytree(src, dest, dirs_exist_ok=True)
        logger.info(
            f"Backed up directory, all subdirectories, and files for {str(src)} to {str(dest)}"
        )
    except shutil.Error as e:
        logger.error(f"Unable to backup {str(src)}")
        logger.exception(e)


def backup_file(src: pathlib.Path, dest: pathlib.Path) -> None:
    """Copy a file from src to dest."""
    try:
        f = pathlib.Path(src).name
        shutil.copyfile(src, (dest / f))
        logger.info(f"Backed up {str(src)} to {str(dest)}")
    except shutil.Error as e:
        logger.error(f"Unable to backup {str(src)}")
        logger.exception(e)


def backup_profile(profile: Profile, backup_dest: pathlib.Path) -> None:
    """Backup a profile."""
    for source in profile.sources:
        src = pathlib.Path(source)
        if pathlib.Path(src).is_file():
            backup_file(src, backup_dest)
        elif pathlib.Path(src).is_dir():
            backup_dir(src, backup_dest)
        else:
            logger.error(
                f"Unable to backup {str(src)} as it is not a file or directory."
            )
