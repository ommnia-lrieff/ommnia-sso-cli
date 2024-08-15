from typing import Annotated, List
from rich.table import Table
from ommnia_sso_cli.shared import console
import asyncio
import typer

from ommnia_sso_cli.data.models.user import RegularUserSchema, UserStatus
from ommnia_sso_cli.data.repositories.users_repository import (
    CreateUserMutationArguments,
    CreateUserMutationFailure,
    CreateUserResponse,
    UsersRepository,
)
from ommnia_sso_cli.state import State

app: typer.Typer = typer.Typer()


@app.command()
def create_regular(
    name: Annotated[str, typer.Argument()],
    email: Annotated[str, typer.Argument()],
    password: Annotated[str, typer.Argument()],
    permissions: Annotated[List[str], typer.Option()] = [],
    groups: Annotated[List[str], typer.Option()] = [],
    status: Annotated[UserStatus, typer.Option()] = UserStatus.ACTIVE,
) -> None:
    # Get the state.
    state: State = State.instance()

    # Create the users repository.
    users_repository: UsersRepository = UsersRepository(state.client)

    # Create the user creation arguments.
    create_user_args: CreateUserMutationArguments = CreateUserMutationArguments(
        name=name,
        email=email,
        password=password,
        permissions=permissions,
        groups=groups,
        status=status,
    )

    # Create the user and handle a failure response.
    create_user_response: CreateUserResponse = asyncio.run(
        users_repository.create_user(create_user_args)
    )
    if isinstance(create_user_response, CreateUserMutationFailure):
        typer.echo(
            f"Failed to create user ({create_user_response.code}): {create_user_response.message}"
        )
        raise typer.Exit(-1)

    # Make sure that the response was successful.
    assert isinstance(
        create_user_response, RegularUserSchema
    ), "If the create user response was not a failure, it should return a user schema."

    table = Table("UID", "Name", "Email", "Status", "Password")
    table.add_row(
        str(create_user_response.uid),
        create_user_response.name,
        create_user_response.email,
        create_user_response.status,
        create_user_response.password_hash,
    )
    console.print(table)
