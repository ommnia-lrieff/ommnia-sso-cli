from dataclasses import dataclass
from enum import Enum
from typing import Annotated, List, Optional, Union
from gql import Client, gql
from graphql import DocumentNode
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from ommnia_sso_cli.data.models.group import GroupSchema

CREATE_GROUP_MUTATION_DOCUMENT: DocumentNode = gql("""
    mutation CreateGroupMutation($args: CreateGroupMutationArguments!) {
        createGroup(args: $args) {
            typename: __typename
            
            ... on GroupSchema {
                description
                name
                uid
            }

            ... on CreateGroupMutationFailure {
                message
                code
            }
        }
    }
""")


@dataclass
class GroupsRepository:
    client: Client

    class CreateGroupMutationArguments(BaseModel):
        model_config = ConfigDict(
            alias_generator=to_camel,
            populate_by_name=True,
            from_attributes=True,
        )

        name: str
        description: Optional[str]
        permissions: List[str]

    class CreateGroupMutationFailureCode(str, Enum):
        PERMISSION_DENIED = "PERMISSION_DENIED"
        NAME_ALREADY_USED = "NAME_ALREADY_USED"

    class CreateGroupMutationFailure:
        model_config = ConfigDict(
            alias_generator=to_camel,
            populate_by_name=True,
            from_attributes=True,
        )

        code: "GroupsRepository.CreateGroupMutationFailureCode"
        message: Optional[str] = None

    class CreateGroupMutationResponse(BaseModel):
        model_config = ConfigDict(
            alias_generator=to_camel,
            populate_by_name=True,
            from_attributes=True,
        )

        create_group: Annotated[
            Union[GroupSchema, "GroupsRepository.CreateGroupMutationFailure"],
            Field(discriminator="typename"),
        ]

    async def create_group(
        self, args: CreateGroupMutationArguments
    ) -> Union[GroupSchema, "GroupsRepository.CreateGroupMutationFailure"]:
        return GroupsRepository.CreateGroupMutationResponse.model_validate(
            await self.client.execute_async(
                CREATE_GROUP_MUTATION_DOCUMENT, {"args": args.model_dump()}
            )
        ).create_group
