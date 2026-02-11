from click.testing import CliRunner as ClickCliRunner


class CliRunner(ClickCliRunner):
    def invoke(self, cli, *args, **kwargs):
        target = getattr(cli, "_app", cli)
        return super().invoke(target, *args, **kwargs)


__all__ = ["CliRunner"]
