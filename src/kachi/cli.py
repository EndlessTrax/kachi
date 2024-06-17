import typer
from typing_extensions import Annotated

from kachi.backup import backup_profile
from kachi.config import Config


app = typer.Typer(no_args_is_help=True)
backup_app = typer.Typer()
app.add_typer(backup_app, name="backup")


def get_version(value: bool):
    if value:
        typer.echo("Kachi v0.1.0")
        raise typer.Exit()


@app.callback()
def cli(
    version: Annotated[
        bool,
        typer.Option("--version", callback=get_version, help="Show current version"),
    ] = False,
):
    """TODO: Add a description here"""
    pass


@backup_app.command()
def backup(
    config: Annotated[str, typer.Option(help="Path to a configuration file")] = "",
    profile: Annotated[str, typer.Option(help="Name of the profile to backup")] = "",
):
    conf = Config(config)
    conf.parse()

    if profile:
        p = conf.get_profile(profile)
        backup_profile(p, p.backup_dest)

    else:
        for p in conf.settings:
            backup_profile(p, p.backup_dest)

    print("Backup complete.")


if __name__ == "__main__":
    typer.run(cli)
