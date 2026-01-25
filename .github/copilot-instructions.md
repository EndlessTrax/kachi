# Kachi AI Instructions

Kachi is a Python-based CLI tool for backing up files/directories defined in YAML configuration profiles.

## Architecture & Core Concepts

- **CLI (`src/kachi/cli.py`)**: Built with `typer`. Entry point is `app`. Handles top-level commands like `backup` and global flags like `--version`.
- **Configuration (`src/kachi/config.py`)**:
  - Parses `config.yaml`.
  - **Profiles**: The core unit. Contains `name`, `sources` (list of paths), and `backup_destination`.
  - **Default Profile Inheritance**: The `default` profile is special. Its `sources` are automatically appended to *all* other profiles. Its `backup_destination` is used if other profiles don't specify one.
- **Backup Logic (`src/kachi/backup.py`)**:
  - Uses `shutil` (`copy2` for files, `copytree` for dirs).
  - **Resilience**: Failures in individual files (e.g., permissions) do *not* crash the whole process. They are logged via `BackupErrorHandler` and skipped.
- **Error Handling (`src/kachi/errors.py`)**: Centralized in `BackupErrorHandler`. Decouples logging logic from backup logic.

## Development Workflows

- **Testing**: Run `pytest`. Configuration in `pyproject.toml` handles coverage (`src/kachi`).
- **Linting/Formatting**: Uses `ruff`.
- **Build**: Uses `nuitka` to build standalone executables (referenced in `pyproject.toml`).

## Code Style & Conventions

- **Path Handling**: ALWAYS use `pathlib.Path` instead of string paths or `os.path`.
- **Logging**: Use the project's `kachi.logger`.
- **Typing**: Use standard Python type hinting.
- **Error Handling**: 
  - Do not suppress exceptions silently.
  - Use `BackupErrorHandler` for operational errors (permissions, missing files) to ensure user feedback without crashing.
- **Config**: When modifying config logic, ensure `default` profile inheritance rules remain consistent.

## Key Files

- `src/kachi/cli.py`: Command definitions.
- `src/kachi/config.py`: YAML parsing and profile merging logic.
- `src/kachi/backup.py`: File system operations.
- `src/kachi/errors.py`: Error handling protocols.
