import click

from config import Config

@click.command()
@click.option('--config', default=None, help='Path to the config file.')
def main(config):
    """TODO: Add docstring here."""
    
    config = Config(config)
    config.parse()

    for profile in config.settings:
        print(profile.name)
        print(profile.sources)
        print(profile.backup_dest)
        print()



if __name__ == '__main__':
    main()