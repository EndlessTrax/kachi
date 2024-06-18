# Kachi

Kachi is a simple tool for backing up valuable files, such as dot files, config files, and any directory you wish to backup. 

By creating a short yaml file, you can declaritively decide what to back up, and where. 

Kachi support "profiles", which allow you to backup different files and directories to different locations, and potentially on different schedules (if you automate it further).

#TODO: Add Image

## Installing

Kachi is deployed as a single executable file that you can download from the releases page. Once downloaded, move it to a location that makes sense for your system and OS, and add to your PATH. 

> NOTE: If a compatable executable for your OS and architecture isn't available, please create an issue to request it, so that it can moved up in priority and added.

## Creating your config file

By default, Kachi looks for a configuration file at `.config/kachi/config.yaml` relative to the users home directory on all systems. You can specify a different configuration location using the `--config` flag (see usage examples below.)

As mentioned above, you can declare different profiles under the top level `profiles` key. Profiles can be named almost alnything you want. The only exception if the `default` profile. While not required, the `default` profile is a handy way of reducing repetition in your configuration file. Any source added to the default profile will be added to all other profiles.

Example:

```yaml
profiles:
  default:
    sources:
      - ".gitconfig"
    backup_destination: "path/to/backup/location/"
    
  profile_1:
    sources:
      - ".bashrc"
```

> NOTE: A fuller example of the config.yaml file can be found in the example folder.

In the above example, if you backup `profile_1`, both the `.gitconfig` and `bashrc` files will be backed up to the default `backup_destination`. If `backup_destination` was declared in `profile_1`, then that would take presidence.

> NOTE: Additional config formats will be added in future (such as `json` or `ini`), but please see issues and upvote any you wish to be added next.

## Usage

To backup the declared sources from your configuration, use the `backup` command with optional flags:

#TODO: Add backup codeblock

Without any flags, all profile will be backed up using a config file in the expected default location. Alternativly specify a single profile to backup with `--profile`:

```shell
kachi backup --profile profile_1 
```

Or specify a configuration to use using `--config`:

```shell
kachi backup --config some/other/path/config.yaml
```

## Contributing

If you find a bug, please file an [issue](https://github.com/EndlessTrax/kachi/issues).

If you have feature requests, please [file an issue](https://github.com/EndlessTrax/kachi/issues) and use the appropriate label.

Please **raise an issue before making a PR**, so that the issue and implementation can be discussed before you write any code. This will save you time, and increase the chances of your PR being merged without significant changes.

Please **lint and format you code** with [ruff](https://github.com/astral-sh/ruff). Use `ruff check .` and `ruff format .` to check and format your code respectively. This will help keep the codebase consistent and maintainable.

Please **include tests** for any PR's that include code (unless current tests cover your code contribution).
