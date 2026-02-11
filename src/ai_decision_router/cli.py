from __future__ import annotations

from pathlib import Path

import typer

from .benchmark import run_benchmark
from .config import RouterConfig, default_config
from .router import DecisionRouter

app = typer.Typer(help="LLM decision router CLI")


def _load_router(config_path: str | None) -> DecisionRouter:
    config = default_config()
    if config_path:
        config = RouterConfig.from_toml(config_path)
    elif Path("router.toml").exists():
        config = RouterConfig.from_toml("router.toml")
    return DecisionRouter(config=config)


@app.command()
def run(prompt: str, config: str | None = typer.Option(None, help="Path to router.toml")) -> None:
    """Route and run a prompt."""
    result = _load_router(config).run(prompt)
    typer.echo(
        f"model={result['chosen_model']} task={result['task_type']} "
        f"latency={result['latency_ms']:.1f}ms"
    )
    typer.echo(result["response"])


@app.command()
def explain(
    prompt: str, config: str | None = typer.Option(None, help="Path to router.toml")
) -> None:
    """Explain route choice without model execution."""
    decision = _load_router(config).explain(prompt)
    typer.echo(
        f"policy={decision.policy} model={decision.model_name} task={decision.task_type}\n"
        f"rationale={decision.rationale}\n"
        f"expected_cost={decision.expected_cost:.6f} "
        f"expected_latency={decision.expected_latency_ms:.1f}ms"
    )


@app.command()
def bench(
    suite: str = typer.Option("quick", help="Benchmark suite: quick|medium"),
    config: str | None = typer.Option(None, help="Path to router.toml"),
) -> None:
    """Run benchmark suite and save reports."""
    report = run_benchmark(_load_router(config), suite=suite)
    typer.echo(
        f"suite={report['suite']} prompts={report['num_prompts']} "
        f"accuracy={report['classifier_accuracy']:.3f}"
    )


if __name__ == "__main__":
    app()
