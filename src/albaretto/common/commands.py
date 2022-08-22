"""
"""

# standard library
from math import floor, log
from typing import List

# typer
from typer import Argument, Context, Option, Typer, echo

# requests
from requests import Response, get


def fetch(
    ctx: Context,
    task_id: str,
    g: List[int] = Option(
        (1, 2, 3, 4),
        max=4,
        help="--g IDs one-indexed from left to right as displayed in the UI."
             " Must type --g <int> for each non-default selection."
             " Example: `--g 3 --g 4` to select the last two images.",
    ),
):
    """
    Fetch images from a DALL·E 2 generation task.

    Args:
        ctx (Context):
        task_id (str):
        g (List[int):
    """
    task_id: str = task_id.split("task-")[-1]
    if len(task_id) != 24:
        raise ValueError

    url: str = f"https://labs.openai.com/api/labs/tasks/task-{task_id}"
    response_task: Response = get(
        url=url,
        headers={
            'Authorization': "Bearer " + ctx.obj.authorization.openai_bearer_token,
            'Content-Type': "application/json",
        },
    )
    generations = set(int(gen)-1 for gen in g)
    for i, generation in enumerate(response_task.json()["generations"]["data"]):
        if i in generations:
            response_image = get(
                url=generation["generation"]["image_path"],
                stream=False,
                headers={
                    'Accept': 'image/webp',
                }
            )
            content_length: int = int(response_image.headers.get('Content-Length'))
            ctx.obj.state[generation['id']] = response_image.content
            echo(f"  ✓ Fetched {generation['id']} ({bytes_to_human_readable(content_length)})")


def bytes_to_human_readable(number_of_bytes: int) -> str:
    magnitude: int = int(floor(log(number_of_bytes, 1024)))
    value: float = number_of_bytes / pow(1024, magnitude)
    if magnitude > 3:
        return f"{value:.1f} TiB"
    return "{:3.2f} {}B".format(value, ("", "Ki", "Mi", "Gi")[magnitude])
