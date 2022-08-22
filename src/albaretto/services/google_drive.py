"""
"""

# standard library
from io import BytesIO

# typer
import typer
from typer import Argument, Context, Option, Typer, echo

# Google services
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# albaretto
from ..common.commands import fetch


app_google_drive: Typer = Typer(
    add_completion=True,
    no_args_is_help=True,
    chain=True,
)

app_google_drive.command()(fetch)


@app_google_drive.command()
def save(
    ctx: Context,
    folder_id: str,
    new: str = Option("", "--new", "-n", help="create a new directory under the parent folder."),
):
    service = build('drive', 'v3', credentials=ctx.obj.authorization.google_drive_credentials)

    if new:
        folder_metadata = {
            'name': new,
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = service.files().create(
            body=folder_metadata,
            fields='id',
        ).execute()
        typer.echo(f"  ✓ Created a new folder '{new}' under {folder_id}.")
        folder_id: str = folder.get("id")

    def upload(name: str, content: bytes):
        file_metadata = {
            'name': name,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(
            fd=BytesIO(content),
            mimetype='image/jpeg',
            resumable=False,
        )
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
        ).execute()

    for key, value in ctx.obj.state.items():
        upload(name=key, content=value)
        echo(f"  ✓ Saved {key}.webp to {folder_id}")
    ctx.obj.state = {}
    echo("Cleared state! Ready for another download from DALL·E 2.")
