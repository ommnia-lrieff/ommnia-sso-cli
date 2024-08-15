import typer

from ommnia_sso_cli.data.repositories.login_repository import (
    LoginRepository,
    RegularLoginFailureResponse,
    RegularLoginRequest,
    RegularLoginResponse,
    RegularLoginSuccessResponse,
)
from ommnia_sso_cli.state import State


async def regular_login(email: str, password: str, token: str) -> str:
    # Create the regular login request.
    regular_login_request: RegularLoginRequest = RegularLoginRequest(
        email=email, password=password, token=token
    )

    # Get the state.
    state: State = State.instance()

    # Create the login repository instance.
    login_repository: LoginRepository = LoginRepository(state.client)

    # Perform the regular login and wait for the response.
    regular_login_response: RegularLoginResponse = await login_repository.regular_login(
        regular_login_request
    )
    if isinstance(regular_login_response, RegularLoginFailureResponse):
        typer.echo(
            f"Failed to perform regular login ({regular_login_response.code}): {regular_login_response.message}"
        )
        raise typer.Exit(-1)

    # Make sure the response was successful.
    assert isinstance(
        regular_login_response, RegularLoginSuccessResponse
    ), "If not a failure, it should always be a success response."

    # Return the bearer.
    return regular_login_response.token
