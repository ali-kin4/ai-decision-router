from ai_decision_router.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_cli_run_smoke() -> None:
    result = runner.invoke(app, ["run", "Write a python function for fizzbuzz"])
    assert result.exit_code == 0
    assert "model=" in result.output


def test_cli_explain_smoke() -> None:
    result = runner.invoke(app, ["explain", "Summarize this essay"])
    assert result.exit_code == 0
    assert "policy=" in result.output
