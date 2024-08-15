from typing import Annotated, List
import typer

app: typer.Typer = typer.Typer()


@app.callback()
def callback() -> None:
    pass


@app.command()
def create(
    name: Annotated[str, typer.Argument()],
    permission: Annotated[List[str], typer.Option()] = [],
) -> None:
    """
    Create a new group.
    """

    pass


@app.command()
def delete(name: Annotated[str, typer.Argument()]) -> None:
    """
    Delete a group.
    """

    pass
