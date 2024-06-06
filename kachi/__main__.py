import click

from kachi.backup import backup_profile
from kachi.config import Config


@click.group()
def cli():
    pass


@click.command()
@click.option("-c", "--config", default=None, help="Path to a configuration file")
@click.option("-p", "--profile", default=None, help="Name of the profile to backup")
def backup(config, profile):
    conf = Config(config)

    if profile:
        p = conf.get_profile(profile)
        backup_profile(p, p.backup_dest)

    else:
        for p in conf.settings:
            backup_profile(p, p.backup_dest)

    print("Backup complete.")


cli.add_command(backup)


if __name__ == "__main__":
    cli()
