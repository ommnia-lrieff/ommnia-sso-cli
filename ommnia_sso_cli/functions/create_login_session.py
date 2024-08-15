from ommnia_sso_tokens import LoginSessionCreationToken, TokenSigner
from typing import List, Optional
import typer

from ommnia_sso_cli.data.repositories.login_repository import (
    CreateLoginSessionFailureResponse,
    CreateLoginSessionResponse,
    CreateLoginSessionSuccessResponse,
    LoginRepository,
)
from ommnia_sso_cli.shared import APP_NAME
from ommnia_sso_cli.state import State


async def create_login_session(
    redirect_url: str,
    required_permissions: List[str] = [],
    optional_permissions: List[str] = [],
    target_app_name: Optional[str] = None,
) -> str:
    # Create the token value.
    token_value: LoginSessionCreationToken = LoginSessionCreationToken(
        app_name=APP_NAME,
        target_app_name=target_app_name,
        required_permissions=required_permissions,
        optional_permissions=optional_permissions,
        redirect_url=redirect_url,
    )

    # Get the state.
    state: State = State.instance()

    # Load the client private key.
    with open(state.config.client_private_key_path, "r") as file:
        client_private_key: str = file.read()

    # Sign the token.
    create_login_session_request_token: str = await TokenSigner().sign(
        token_value, client_private_key
    )

    # Create the login repository instance.
    login_repository: LoginRepository = LoginRepository(state.client)

    # Create the login session and handle failures.
    create_login_session_response: CreateLoginSessionResponse = (
        await login_repository.create_login_session(create_login_session_request_token)
    )
    if isinstance(create_login_session_response, CreateLoginSessionFailureResponse):
        typer.echo(
            f"Failed to create login session ({create_login_session_response.code}): {create_login_session_response.message}"
        )
        raise typer.Exit(-1)

    # Make sure the response was successful.
    assert isinstance(
        create_login_session_response, CreateLoginSessionSuccessResponse
    ), "If not a failure, it should always be a success response."

    # Return the token.
    return create_login_session_response.token
