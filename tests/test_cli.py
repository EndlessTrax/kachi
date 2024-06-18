from typer.testing import CliRunner

from kachi.cli import app

runner = CliRunner()


class TestCli:
    def test_get_version(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "kachi" in result.stdout
   