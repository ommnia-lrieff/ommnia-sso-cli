from typing import Annotated, List
from ommnia_sso_tokens.token_signer import asyncio
import typer

from ommnia_sso_cli.functions import create_login_session

app: typer.Typer = typer.Typer()


@app.command()
def create_session(
    target_app_name: Annotated[str, typer.Argument()],
    redirect_url: Annotated[str, typer.Option()],
    required_permissions: Annotated[List[str], typer.Option()] = [],
    optional_permissions: Annotated[List[str], typer.Option()] = [],
):
    # Create the login session and get the token.
    token: str = asyncio.run(
        create_login_session(
            redirect_url,
            target_app_name=target_app_name,
            required_permissions=required_permissions,
            optional_permissions=optional_permissions,
        )
    )

    # Print the success response.
    typer.echo(
        f"Login session created successfully, token: {typer.style(token, fg="green", bold=True)}"
    )
