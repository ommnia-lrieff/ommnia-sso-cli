from dataclasses import dataclass
from enum import Enum
from typing import Annotated, List, Literal, Optional, Union
from gql import Client, gql
from graphql import DocumentNode
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from ommnia_sso_cli.data.models.user import RegularUserSchema, UserStatus


CREATE_USER_MUTATION_DOCUMENT: DocumentNode = gql("""
    mutation CreateUserMutation($args: CreateUserMutationArguments!) {
        createUser(args: $args) {
            typename: __typename

            ... on RegularUserSchema {
                email
                name
                passwordHash
                status
                uid
            }

            ... on CreateUserMutationFailure {
                message
                code
            }
        }
    }
""")


class CreateUserMutationArguments(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    name: str
    email: str
    password: str
    permissions: List[str]
    groups: List[str]
    status: UserStatus


class CreateUserMutationFailureCode(str, Enum):
    PERMISSION_DENIED = "PERMISSION_DENIED"
    EMAIL_ALREADY_USED = "EMAIL_ALREADY_USED"
    GROUP_NOT_FOUND = "GROUP_NOT_FOUND"


class CreateUserMutationFailure(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    typename: Literal["CreateUserMutationFailure"] = "CreateUserMutationFailure"
    code: "CreateUserMutationFailureCode"
    message: Optional[str]


CreateUserResponse = Annotated[
    Union[RegularUserSchema, "CreateUserMutationFailure"],
    Field(discriminator="typename"),
]


class CreateUserMutationResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    create_user: CreateUserResponse


@dataclass
class UsersRepository:
    client: Client

    async def create_user(
        self, args: CreateUserMutationArguments
    ) -> Union[RegularUserSchema, "CreateUserMutationFailure"]:
        return CreateUserMutationResponse.model_validate(
            await self.client.execute_async(
                CREATE_USER_MUTATION_DOCUMENT, {"args": args.model_dump()}
            )
        ).create_user
