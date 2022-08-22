"""
"""

# standard library
from pathlib import Path

# typer
from typer import Argument, Context, Option, Typer, echo

# albaretto
from ..common.commands import fetch

app_local_filesystem: Typer = Typer(
    add_completion=True,
    no_args_is_help=True,
    chain=True,
)

app_local_filesystem.command()(fetch)


@app_local_filesystem.command()
def save(
    ctx: Context,
    directory: str = Argument("./", help="an output directory"),
):
    for key, value in ctx.obj.state.items():
        with Path(f"{directory}/{key}.webp").open("wb") as f:
            f.write(value)
            echo(f"  ✓ Saved {key}.webp to {directory}")
    ctx.obj.state = {}
    echo("Cleared state! Ready for another download from DALL·E 2.")
