# Kachi AI Instructions

## Project Overview

Kachi is a Python 3.14+ CLI tool for declarative backup of files and directories. Users define what to back up (and where) in YAML configuration profiles. Kachi is distributed as a standalone executable built with Nuitka — no Python runtime required on the target machine.

**Current version**: `0.1.14` (defined in `src/kachi/__init__.py`).

### Design Philosophy

- **Simplicity first**: Kachi is intentionally minimal. It copies files — no compression, no encryption, no cloud sync. Features are added conservatively and must serve the core "declarative backup" use case.
- **Declarative configuration**: All backup behavior is driven by a YAML config file. The user describes *what* and *where*; Kachi does the rest.
- **Resilience over correctness**: A single file failure (permissions, missing source) must never crash the entire backup run. Errors are logged and skipped so the remaining sources still get backed up.
- **Cross-platform**: Must work on both Windows and Linux. All path handling uses `pathlib.Path`, never string concatenation or `os.path`.

---

## Architecture

### Module Map

| Module | Responsibility |
|---|---|
| `src/kachi/__init__.py` | Package root. Defines `__version__`, configures `logging` with a custom `RichHandler` (`KachiLogHandler`), and exports the module-level `logger`. |
| `src/kachi/__main__.py` | Entry point for `python -m kachi`. Calls `app()` from `cli`. |
| `src/kachi/cli.py` | CLI layer built with **Typer**. Defines the `app` and all commands/flags. Currently has one command (`backup`) and a global `--version` flag. |
| `src/kachi/config.py` | YAML parsing via **PyYAML**. Contains the `Config` class (file location handling), `Settings` class (parsing), and `Profile` dataclass. Implements default-profile inheritance logic. |
| `src/kachi/backup.py` | File-system operations. `backup_file` (uses `shutil.copy2`), `backup_dir` (uses `shutil.copytree`), `backup_profile` (orchestrates a profile's sources), and `log_not_found`. Returns `(not_found_list, success_count, error_count)` tuples for summary reporting. |
| `src/kachi/errors.py` | `BackupErrorHandler` class. Decouples error-logging logic from backup logic. Accepts any logger satisfying the `ErrorLogger` protocol. Handles permission errors, shutil errors, file-not-found, and invalid destinations. |

### Key Data Structures

- **`Profile`** (dataclass in `config.py`): `name: str`, `sources: list[Path]`, `backup_destination: Path | None`.
- **`Config`**: Manages filepath resolution (defaults to `~/.config/kachi/config.yaml`). `parse()` populates `self.settings` with a list of `Profile` objects.
- **`Settings`**: Internal parser. Reads YAML, applies default-profile inheritance, returns `list[Profile]`.

### Default Profile Inheritance Rules

The `default` profile has special semantics — these rules are **critical** and must be preserved:

1. If a `default` profile exists, its `sources` are **appended** to every other profile's sources.
2. If another profile does **not** declare a `backup_destination`, it inherits the default's `backup_destination`.
3. If a profile declares its own `backup_destination`, it takes precedence over the default.
4. The `default` profile itself is also backed up as a standalone profile.

### Error Handling Pattern

- `BackupErrorHandler` is instantiated once at module level in `backup.py`.
- Individual backup functions (`backup_file`, `backup_dir`) catch specific exceptions (`PermissionError`, `shutil.Error`, `OSError`) and delegate to the handler, returning `bool` to indicate success/failure.
- `FileNotFoundError` is re-raised (not caught) so it can be handled at the profile level as a "source not found" case.
- The CLI layer in `cli.py` aggregates counts and logs a final summary line.

### Logging

- Uses Python's `logging` module with a custom `RichHandler` subclass (`KachiLogHandler`) that formats levels as `[LEVEL]`.
- The module-level `logger` from `src/kachi/__init__.py` is imported and used everywhere: `from kachi import logger`.
- Output goes to stderr via Rich. No file-based logging currently.

---

## Development

### Toolchain

| Tool | Purpose |
|---|---|
| **uv** | Package/environment management. All CI uses `uv sync --all-extras --dev` and `uv run`. |
| **pytest** | Testing. Config in `pyproject.toml` adds `--cov` flags automatically. Tests live in `tests/`. |
| **ruff** | Linting (`select = ["I", "E"]`) and formatting. Run `ruff check .` and `ruff format .`. |
| **Nuitka** | Builds standalone executables for Windows and Linux (x64). Triggered by version tags in CI. |

### Running Locally

```bash
uv sync --all-extras --dev   # install deps
uv run pytest                # run tests with coverage
uv run ruff check .          # lint
uv run ruff format .         # format
```

### CI / GitHub Actions

- **`test.yml`**: Runs pytest on push/PR to `main`. Python 3.14, Ubuntu.
- **`lint.yml`**: Runs ruff on push/PR to `main`.
- **`build.yml`**: Triggered on version tags (`v*.*.*`). Builds executables for Ubuntu and Windows via Nuitka, generates checksums, and creates a GitHub Release with all artifacts.

### Testing Conventions

- Tests use `pytest` with `tmp_path` fixtures for filesystem operations.
- CLI tests use `typer.testing.CliRunner`.
- Mocking is done with `unittest.mock.patch` where needed.
- Test files mirror source files: `test_backup.py`, `test_cli.py`, `test_config.py`, `test_errors.py`.
- All new features and bug fixes **must** include tests.

---

## Code Style & Conventions

- **Paths**: ALWAYS use `pathlib.Path`. Never `os.path`, never raw strings for filesystem paths.
- **Logging**: Always use `from kachi import logger`. Never `print()` for user-facing output (except the `--version` flag).
- **Type hints**: Use standard Python type hinting throughout. Use `X | None` union syntax (not `Optional[X]`).
- **Error handling**:
  - Never suppress exceptions silently.
  - Use `BackupErrorHandler` for operational errors (permissions, missing files) to provide user feedback without crashing.
  - Raise exceptions for programmer errors (bad config, invalid state).
- **Docstrings**: Use Google-style docstrings with `Args:` and `Returns:` sections.
- **Config changes**: When modifying config/parsing logic, ensure the default profile inheritance rules above remain intact. Add tests that verify inheritance behavior.

---

## Roadmap & Planned Features

The following are open feature requests tracked as GitHub issues. When implementing any of these, reference the corresponding issue number in commits and PRs.

### Incremental / Change-Only Backup ([#32](https://github.com/EndlessTrax/kachi/issues/32))

Only copy files that have actually changed since the last backup. This could use modification timestamps (`st_mtime`) or content hashing to detect changes. This has significant performance implications for large backup sets.

### Verbosity Control ([#31](https://github.com/EndlessTrax/kachi/issues/31))

Allow the user to toggle logging verbosity via a CLI flag (e.g., `--verbose` / `--quiet` / `-v`). Currently all output is at `INFO` level. This should integrate with the existing `logging` setup and `RichHandler`.

### Progress Bar for Large Operations ([#28](https://github.com/EndlessTrax/kachi/issues/28))

Add a visual progress indicator (using Rich's progress bar) for large file/directory copies. Should respect the verbosity setting once implemented.

### CLI Profile Management ([#15](https://github.com/EndlessTrax/kachi/issues/15))

Add commands to add/remove sources and set `backup_destination` for a profile directly from the CLI, instead of requiring manual YAML editing. This would likely be a new `profile` command group (e.g., `kachi profile add-source`, `kachi profile set-destination`).

### JSON Config Format Support ([#14](https://github.com/EndlessTrax/kachi/issues/14))

Support JSON as an alternative config file format alongside YAML. The config parser would need to detect the format (by extension or content) and delegate to the appropriate parser.

### Restore Command ([#13](https://github.com/EndlessTrax/kachi/issues/13))

A `restore` command that reverses the backup operation — copying files from the backup destination back to their original source locations. This is the inverse of `backup` and would reuse the same profile definitions.

---

## Important Implementation Notes

- **Entry point**: The CLI entry point is `kachi.cli:app` (defined in `pyproject.toml` under `[project.scripts]`).
- **Default config path**: `~/.config/kachi/config.yaml` (defined as `DEFAULT_CONFIG_PATH` in `config.py`). This is the same on both Windows and Linux.
- **Dependencies**: Only two runtime dependencies — `typer` and `pyyaml`. `rich` is pulled in transitively by `typer`. Keep the dependency footprint minimal.
- **Python version**: Requires Python 3.14+ (`requires-python = ">=3.14"` in `pyproject.toml`).
- **Build output**: Nuitka produces a single-file executable. The `__main__.py` exists to support `python -m kachi` during development.
- **Version management**: The version string lives in `src/kachi/__init__.py` as `__version__`. It is also referenced in `cli.py` for the `--version` flag. Keep these in sync.
