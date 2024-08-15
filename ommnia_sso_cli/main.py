import asyncio
from typing import Annotated, Optional
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
import typer

from ommnia_sso_cli.apps import groups, login, users
from ommnia_sso_cli.data.models import AuthConfigModel, ConfigModel
from ommnia_sso_cli.data.repositories.config_repository import ConfigRepository
from ommnia_sso_cli.functions import create_login_session, regular_login
from ommnia_sso_cli.shared import APP_NAME
from ommnia_sso_cli.state import State

app: typer.Typer = typer.Typer()


@app.callback()
def load_config(ctx: typer.Context):
    # If we're running the setup command, skip the standard initialization procedure.
    if ctx.invoked_subcommand in ["setup", "login"]:
        return

    # Read the configuration file.
    config: Optional[ConfigModel] = ConfigRepository(APP_NAME).load()
    if config is None:
        typer.secho("Could not read configuration file", fg="red")
        raise typer.Exit(-1)

    # Create the GraphQL client
    client: Client = Client(transport=AIOHTTPTransport(config.graphql_endpoint_url))

    # Put the client and the config in the state.
    state: State = State.instantiate(client, config)

    # Create a login token then perform a regular login.
    login_token: str = asyncio.run(create_login_session("", required_permissions=["ommnia_sso"]))
    bearer_token: str = asyncio.run(
        regular_login(state.config.auth.email, state.config.auth.password, login_token)
    )

    # Recreate the client now with the authorization header.
    state.client = Client(
        transport=AIOHTTPTransport(
            url=config.graphql_endpoint_url,
            headers={
                "Authorization": f"Bearer {bearer_token}",
            },
        )
    )


app.add_typer(groups.app, name="groups")
app.add_typer(login.app, name="login")
app.add_typer(users.app, name="users")


@app.command()
def setup(
    graphql_endpoint_url: Annotated[str, typer.Option(prompt=True)],
    client_private_key_file_path: Annotated[str, typer.Option(prompt=True)],
    server_public_key_file_path: Annotated[str, typer.Option(prompt=True)],
    email: Annotated[str, typer.Option(prompt=True)],
    password: Annotated[str, typer.Option(prompt=True)],
    app_name: Annotated[
        str,
        typer.Option(
            prompt=True, help="The name under which the server will know the current CLI app."
        ),
    ],
):
    ConfigRepository(APP_NAME).save(
        ConfigModel(
            app_name=app_name,
            graphql_endpoint_url=graphql_endpoint_url,
            client_private_key_path=client_private_key_file_path,
            server_public_key_path=server_public_key_file_path,
            auth=AuthConfigModel(
                email=email,
                password=password,
            ),
        )
    )


if __name__ == "__main__":
    app()
