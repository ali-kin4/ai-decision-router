"""Small Typer-compatible interface built on Click for offline environments."""

from __future__ import annotations

import click


def Option(default=None, *args, **kwargs):
    return default


def echo(message: str) -> None:
    click.echo(message)


class Typer:
    def __init__(self, help: str | None = None):
        self._app = click.Group(help=help)

    def command(self, *args, **kwargs):
        def decorator(func):
            params = []
            annotations = func.__annotations__
            defaults = func.__defaults__ or ()
            positional = list(func.__code__.co_varnames[: func.__code__.co_argcount])
            defaults_offset = len(positional) - len(defaults)
            defaults_map = {
                positional[i + defaults_offset]: defaults[i] for i in range(len(defaults))
            }

            for name in positional:
                ann = annotations.get(name, str)
                default = defaults_map.get(name, None)
                click_type = click.STRING
                if ann in [int, float]:
                    click_type = click.INT if ann is int else click.FLOAT
                if default is None and name not in defaults_map:
                    params.append(click.Argument([name], type=click_type))
                else:
                    params.append(
                        click.Option(
                            [f"--{name.replace('_', '-')}", name], default=default, type=click_type
                        )
                    )

            cmd = click.Command(func.__name__.replace("_", "-"), params=params, callback=func)
            self._app.add_command(cmd)
            return func

        return decorator

    @property
    def name(self):
        return self._app.name

    def __getattr__(self, item):
        return getattr(self._app, item)

    def __call__(self, *args, **kwargs):
        return self._app(*args, **kwargs)
