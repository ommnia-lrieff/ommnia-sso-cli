from dataclasses import dataclass
from typing import ClassVar, Optional, Type

from gql import Client

from ommnia_sso_cli.data.models import ConfigModel


@dataclass
class State:
    _instance: ClassVar[Optional["State"]] = None

    client: Client
    config: ConfigModel

    @classmethod
    def instantiate(cls: Type["State"], client: Client, config: ConfigModel) -> "State":
        assert cls._instance is None, "The instance should not be instantiated more than once"
        cls._instance = State(client, config)
        return cls._instance

    @classmethod
    def instance(cls: Type["State"]) -> "State":
        assert cls._instance is not None, "The instance has not been instantiated"
        return cls._instance
