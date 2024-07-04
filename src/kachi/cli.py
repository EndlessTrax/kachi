from pathlib import Path

import typer
from typing_extensions import Annotated

from kachi import __version__ as kachi_version
from kachi import logger
from kachi.backup import backup_profile, log_not_found
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
    pass  # pragma: no cover


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
        try:
            p = conf.get_profile(profile)
        except ValueError as e:
            logger.error(e)
            raise typer.Exit(code=1)

        not_found = backup_profile(p)

        if len(not_found) > 0:
            logger.warning(f"{len(nf)} sources not backed up.")

    else:
        not_found = []
        for p in conf.settings:
            nf = backup_profile(p)
            not_found.extend(nf)

    log_not_found(not_found)
    typer.Exit(code=0)


if __name__ == "__main__":
    typer.run(cli)  # pragma: no cover
