import pathlib
import shutil


def backup_file(src: str, dest: str):
    """Copy a file from src to dest."""
    try:
        shutil.copyfile(src, dest)
        print(f"Successfully backedup {src} to {dest}")
    except shutil.Error as e:
        print(f"Unable to backup {src} due to: {e}")


def backup_dir(src: str, dest: str):
    """Copy a directory from src to dest."""
    try:
        shutil.copytree(src, dest)
        print(f"Successfully backedup {src} to {dest}")
    except shutil.Error as e:
        print(f"Unable to backup {src} due to: {e}")


def backup_profile(profile, backup_dest):
    """Backup a profile."""
    for src in profile.sources:
        if pathlib.Path(src).is_file():
            backup_file(src, backup_dest)
        elif pathlib.Path(src).is_dir():
            backup_dir(src, backup_dest)
        else:
            print(f"Unable to backup {src}. File or directory not found.")
