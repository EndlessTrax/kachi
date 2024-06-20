from pathlib import Path

import typer
from typing_extensions import Annotated

from kachi import __version__ as kachi_version
from kachi import logger
from kachi.backup import backup_profile
from kachi.config import Config

app = typer.Typer(no_args_is_help=True)


def get_version(value: bool):
    if value:
        print(f"kachi v{kachi_version}")
        raise typer.Exit()


@app.callback()
def cli(
    version: Annotated[
        bool,
        typer.Option("--version", callback=get_version, help="Show current version"),
    ] = False,
):
    """Kachi is a simple tool for backing up valuable files."""
    pass


@app.command()
def backup(
    config: Annotated[str, typer.Option(help="Path to a configuration file")] = "",
    profile: Annotated[str, typer.Option(help="Name of the profile to backup")] = "",
):
    """Backup files and directories.

    If no profile is specified, all profiles in the configuration file
    will be backed up. If no configuration file is specified, the
    default configuration file path will be used.
    """

    logger.info("Starting backup...")

    conf = Config(config)
    conf.parse()

    if profile:
        logger.info(f"Backing up profile: {profile}")
        p = conf.get_profile(profile)
        if p is None:
            logger.error(f"Profile: {profile} not found.")
            raise typer.Exit(code=1)

        nf = backup_profile(p, Path(p.backup_destination))

        if len(nf) > 0:
            logger.warning(f"{len(nf)} sources not backed up.")

    else:
        total_nf = []
        for p in conf.settings:
            logger.info(f"Backing up profile: {p.name}")
            nf = backup_profile(p, Path(p.backup_destination))
            total_nf.extend(nf)

        if len(total_nf) > 0:
            logger.warning(f"{len(total_nf)} sources not backed up.")


if __name__ == "__main__":
    typer.run(cli)
