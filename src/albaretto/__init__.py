"""
"""

# standard library
from json import loads as json_loads
from dataclasses import dataclass, field
from typing import Final, Optional, Tuple, Union, List

# typer
from typer import Argument, Context, Option, Typer, echo

# Google services
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# albaretto
from .common.subshell import make_subshell
from .services.google_drive import app_google_drive
from .services.local_filesystem import app_local_filesystem


# https://developers.google.com/identity/protocols/oauth2/scopes#drive
SCOPES: Final[Tuple[str, ...]] = (
    "https://www.googleapis.com/auth/drive.metadata",
    "https://www.googleapis.com/auth/drive",
)

app: Typer = Typer(
    add_completion=True,
    no_args_is_help=True,
    chain=True,
)
app.add_typer(app_google_drive)
app.add_typer(app_local_filesystem)


_warning_openai_terms_of_service: Final[str] = \
    "Programmatically accessing DALL·E 2 may be against OpenAI's terms of service." \
    " Proceed at your own risk."


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
@dataclass
class Authorization:
    openai_bearer_token: str
    google_drive_token: Optional[dict] = None
    google_drive_credentials: Optional[Credentials] = None


@dataclass
class StateStore:
    authorization: Authorization
    state: dict = field(default_factory=dict)


@app.callback()
def albaretto(
    ctx: Context,
    openai_bearer_token: str = Argument(..., help="a 24-character bearer token"),
):
    """
    Programmatically download images from OpenAI's DALL·E 2 web interface.
    """
    if not isinstance(openai_bearer_token, str):
        raise ValueError(
            f"`openai_bearer_token` must be a string with a length of 45 characters beginning with `sess-`"
            f" (received {type(openai_bearer_token)=})"
        )
    if len(openai_bearer_token) != 45:
        raise ValueError(
            f"`openai_bearer_token` must be a string with a length of 45 characters beginning with `sess-`"
            f" (received {len(openai_bearer_token)=})"
        )
    if not openai_bearer_token.startswith("sess-"):
        raise ValueError(
            f"`openai_bearer_token` must be a string with a length of 45 characters beginning with `sess-`"
            f" (received {openai_bearer_token})"
        )
    ctx.obj = StateStore(authorization=Authorization(openai_bearer_token=openai_bearer_token))


@app.command()
def google_drive(
    ctx: Context,
    path_credentials_json: str = Argument(..., help="Google Drive credentials"),
) -> None:
    """
    TODO: move authorization and session construction into different functions
    """
    creds = ctx.obj.authorization.google_drive_credentials
    if ctx.obj.authorization.google_drive_token:
        creds = Credentials.from_authorized_user_info(info=ctx.obj.authorization.google_drive_token, scopes=SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # TODO: check for path existence
            flow = InstalledAppFlow.from_client_secrets_file(path_credentials_json, SCOPES)
            creds = flow.run_local_server(port=0)
        ctx.obj.authorization.google_drive_token = json_loads(creds.to_json())
    ctx.obj.authorization.google_drive_credentials = creds

    shell = make_subshell(
        typer_instance=app_google_drive,
        ctx=ctx,
        prompt="[albaretto] [google-drive] > ",
        intro=_warning_openai_terms_of_service
    )
    shell.cmdloop()


@app.command()
def local_filesystem(
    ctx: Context,
) -> None:
    shell = make_subshell(
        typer_instance=app_local_filesystem,
        ctx=ctx,
        prompt="[albaretto] [local-filesystem] > ",
        intro=_warning_openai_terms_of_service
    )
    shell.cmdloop()


if __name__ == "__main__":
    app()
