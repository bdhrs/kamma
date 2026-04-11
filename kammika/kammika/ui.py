from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text
from rich.theme import Theme

_THEME = Theme(
    {
        "banner": "#c57b39 bold",
        "info": "#c08a52",
        "muted": "#9b7b5b",
        "question": "#d59a5a bold",
        "input": "#f0c48a bold",
        "success": "#d48b3a bold",
        "warning": "#b9824a bold",
        "error": "#a2552d bold",
        "panel.border": "#8a5a34",
        "panel.title": "#d59a5a bold",
    }
)

console = Console(theme=_THEME)


def gap() -> None:
    console.print()


def show_banner(text: str) -> None:
    gap()
    console.print(Text(text.strip("\n"), style="banner"))
    gap()


def info(message: str) -> None:
    console.print(f"[info]{message}[/info]")


def muted(message: str) -> None:
    console.print(f"[muted]{message}[/muted]")


def success(message: str) -> None:
    console.print(f"[success]{message}[/success]")


def warning(message: str) -> None:
    console.print(f"[warning]{message}[/warning]")


def error(message: str) -> None:
    console.print(f"[error]{message}[/error]")


def section(title: str) -> None:
    gap()
    console.print(f"[panel.title]{title}[/panel.title]")
    gap()


def prompt_text(message: str, default: str | None = None) -> str:
    console.print(f"[question]{message}[/question]")
    value = Prompt.ask("[input]›[/input]", default=default or "", console=console)
    gap()
    return value


def prompt_confirm(message: str, default: bool = True) -> bool:
    console.print(f"[question]{message}[/question]")
    value = Confirm.ask("[input]›[/input]", default=default, console=console, show_choices=True)
    gap()
    return value


def warm_panel(body: str, title: str) -> Panel:
    return Panel(body, title=title, border_style="panel.border", title_align="left", expand=False)
