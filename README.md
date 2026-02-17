![GitHub Release](https://img.shields.io/github/v/release/endlesstrax/kachi)
![GitHub branch check runs](https://img.shields.io/github/check-runs/endlesstrax/kachi/main)

# Kachi

Kachi is a simple tool for backing up valuable files, such as dotfiles, config files, and any directory you wish to backup. 

By creating a short yaml file, you can declaratively decide what to back up, and where. 

Kachi uses "profiles", which allow you to backup different files and directories to different locations, and potentially on different schedules (if you automate it further).

```txt
➜ .\kachi.exe --help

 Usage: kachi.exe [OPTIONS] COMMAND [ARGS]...

 Kachi is a simple tool for backing up valuable files.

╭─ Options ────────────────────────────────────────────────────────────────────────────╮
│ --version                Show current version                                   
│ --install-completion     Install completion for the current shell.              
│ --show-completion        Show completion for the current shell, to copy it or   
│                          customize the installation.                            
│ --help                   Show this message and exit.                            
╰──────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────╮
│ backup   Backup files and directories.                                          
╰──────────────────────────────────────────────────────────────────────────────────────╯
```

## Installing

### Quick Install (Linux)

For Linux x64 systems, you can use the installation script to automatically download and install the latest version:

**Option 1: One-liner (requires trust)**
```bash
curl -fsSL https://raw.githubusercontent.com/EndlessTrax/kachi/main/install.sh | bash
```

**Option 2: Inspect before running (recommended)**
```bash
curl -fsSL https://raw.githubusercontent.com/EndlessTrax/kachi/main/install.sh -o install.sh
# Inspect the script
cat install.sh
# Run it if you're satisfied
bash install.sh
```

This will download the latest release for your system and install it to `~/.local/bin/kachi`. Make sure `~/.local/bin` is in your `PATH`.

### Manual Installation

Kachi is deployed as a single executable file that you can [download from the releases page](https://github.com/EndlessTrax/kachi/releases). Once downloaded, move it to a location that makes sense for your system and OS, and add it to your PATH. 

> NOTE: If a compatable executable for your OS and architecture isn't available, please create an issue or upvote a current one so it can moved up in priority and added to future releases.

## Configuration

By default, Kachi looks for a configuration file at `.config/kachi/config.yaml` relative to the user's home directory on all systems. You can specify a different configuration location using the `--config` flag (see usage example below.)

As mentioned above, you can declare different profiles under the top-level `profiles` key. Profiles can be named almost anything you want. The only exception is the `default` profile. While not required, the `default` profile is a handy way of reducing repetition in your configuration file. Any source added to the default profile will be added to all other profiles automatically when backed up.

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

> NOTE: A fuller [example of the config.yaml](examples\example.yaml) file can be found in the example folder.

In the above example, if you backup `profile_1`, both the `.gitconfig` and `.bashrc` files will be backed up to the default `backup_destination`. If a `backup_destination` was declared in `profile_1`, then that would take precedence.

> NOTE: Additional config formats will be added in future (such as `json` or `ini`), but please see issues and upvote any you wish to be added next to help prioritize formats.

## Usage

To back up the declared sources from your configuration, use the `backup` command with optional flags:

```txt
➜ .\kachi.exe backup --help

 Usage: kachi.exe backup [OPTIONS]

 Backup files and directories.
 If no profile is specified, all profiles in the configuration file will be backed up.
 If no configuration file is specified, the default configuration file path will be
 used.

╭─ Options ────────────────────────────────────────────────────────────────────────────╮
│ --config         TEXT  Path to a configuration file                                  
│ --profile        TEXT  Name of the profile to backup                                 
│ --help                 Show this message and exit.                                   
╰──────────────────────────────────────────────────────────────────────────────────────╯
```

Without any flags, all profiles will be backed up using a config file in the expected default location. Alternatively, specify a single profile to backup with `--profile`:

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

Please **raise an issue before making a PR**, so that the issue and implementation can be discussed before you write any code. This will save you time, and increase the chances of your PR being merged without significant changes. And please **include tests** for any PRs that include code (unless current tests cover your code contribution).

Please **lint and format your code** with [ruff](https://github.com/astral-sh/ruff). This will help keep the codebase consistent and maintainable.
