import json

import typer

from kammika import __version__
from kammika.config import KammikaConfig
from kammika.paths import config_path
from kammika.ui import console

app = typer.Typer(
    name="kammika",
    help="Autonomous kamma orchestrator — picks the next issue and launches an agent session.",
    no_args_is_help=False,
)
def version_callback(value: bool) -> None:
    if value:
        console.print(f"[info]kammika {__version__}[/info]")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    if ctx.invoked_subcommand is not None:
        return

    cfg_path = config_path()
    needs_init = True
    if cfg_path.exists():
        try:
            KammikaConfig.from_dict(json.loads(cfg_path.read_text()))
            needs_init = False
        except (json.JSONDecodeError, KeyError, TypeError):
            needs_init = True

    if needs_init:
        from kammika.commands.init import run_init

        run_init(show_next=False)

    from kammika.commands.run import run_cycle

    run_cycle()


@app.command()
def init() -> None:
    """Set up kammika in the current repo."""
    from kammika.commands.init import run_init

    run_init()


@app.command()
def triage() -> None:
    """Pick the next issue to work on and write it to the queue."""
    from kammika.commands.triage import run_triage

    run_triage()


@app.command()
def run() -> None:
    """Triage → branch → launch agent. Loops until Ctrl-C or no issues remain."""
    from kammika.commands.run import run_cycle

    run_cycle()


if __name__ == "__main__":
    app()
