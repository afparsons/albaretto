"""
"""

# typer
from typer import Typer
from typer.models import CommandInfo
from typer.main import get_command_from_info
from click_shell.core import ClickShell


def make_subshell(
    typer_instance: Typer,
    ctx,
    prompt=None,
    intro=None,
    hist_file=None
) -> ClickShell:
    """
    Create a subshell. Derived from click-shell.

    Args:
        typer_instance (Typer):
        ctx:
        prompt:
        intro (str):
        hist_file:

    Returns:
        A ClickShell instance.
    """

    ctx.info_name = None
    shell = ClickShell(ctx=ctx, hist_file=hist_file)

    if prompt is not None:
        shell.prompt = prompt

    if intro is not None:
        shell.intro = intro

    for command_info in typer_instance.registered_commands:  # type: CommandInfo
        command = get_command_from_info(command_info, pretty_exceptions_short=False, rich_markup_mode="rich")
        shell.add_command(command, command.name)

    return shell
