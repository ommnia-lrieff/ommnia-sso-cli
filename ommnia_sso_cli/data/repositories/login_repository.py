from dataclasses import dataclass
from typing import Annotated, Literal, Optional, Union
from gql import Client, gql
from graphql import DocumentNode
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


CREATE_LOGIN_SESSION_MUTATION: DocumentNode = gql("""
    mutation CreateLoginSession($requestToken: String!) {
        createLoginSession(requestToken: $requestToken) {
            typename: __typename
            
            ... on CreateLoginSessionFailureResponse {
                message
                code
            }

            ... on CreateLoginSessionSuccessResponse {
                __typename
                token
            }
        }
    }
""")


class CreateLoginSessionFailureCode(Enum):
    INVALID_REQUEST_TOKEN = "INVALID_REQUEST_TOKEN"
    SERVER_ERROR = "SERVER_ERROR"


class CreateLoginSessionFailureResponse(BaseModel):
    typename: Literal["CreateLoginSessionFailureResponse"] = "CreateLoginSessionFailureResponse"
    code: CreateLoginSessionFailureCode
    message: Optional[str]


class CreateLoginSessionSuccessResponse(BaseModel):
    typename: Literal["CreateLoginSessionSuccessResponse"] = "CreateLoginSessionSuccessResponse"
    token: str


CreateLoginSessionResponse = Annotated[
    Union[CreateLoginSessionFailureResponse, CreateLoginSessionSuccessResponse],
    Field(discriminator="typename"),
]


class CreateLoginSessionMutationResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    create_login_session: CreateLoginSessionResponse


REGULAR_LOGIN_MUTATION: DocumentNode = gql("""
    mutation RegularLoginMutation($request: RegularLoginRequest!) {
        regularLogin(request: $request) {
            typename: __typename

            ... on RegularLoginSuccessResponse {
                token
            }

            ... on RegularLoginFailureResponse {
                message
                code
            }
        }
    }
""")


class RegularLoginRequest(BaseModel):
    email: str
    password: str
    token: str


class RegularLoginFailureCode(Enum):
    USER_NOT_FOUND = "USER_NOT_FOUND"
    WRONG_PASSWORD = "WRONG_PASSWORD"
    USER_NOT_ACTIVE = "USER_NOT_ACTIVE"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    INVALID_TOKEN = "INVALID_TOKEN"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_COMLETED = "SESSION_COMPLETED"
    SESSION_EXPIRED = "SESSION_EXPIRED"


class RegularLoginFailureResponse(BaseModel):
    typename: Literal["RegularLoginFailureResponse"] = "RegularLoginFailureResponse"
    code: RegularLoginFailureCode
    message: Optional[str]


class RegularLoginSuccessResponse(BaseModel):
    typename: Literal["RegularLoginSuccessResponse"] = "RegularLoginSuccessResponse"
    token: str


RegularLoginResponse = Annotated[
    Union[RegularLoginFailureResponse, RegularLoginSuccessResponse],
    Field(discriminator="typename"),
]


class RegularLoginMutationResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    regular_login: RegularLoginResponse


@dataclass
class LoginRepository:
    client: Client

    async def create_login_session(self, request_token: str) -> CreateLoginSessionResponse:
        return CreateLoginSessionMutationResponse.model_validate(
            await self.client.execute_async(
                CREATE_LOGIN_SESSION_MUTATION, {"requestToken": request_token}
            )
        ).create_login_session

    async def regular_login(self, request: RegularLoginRequest) -> RegularLoginResponse:
        return RegularLoginMutationResponse.model_validate(
            await self.client.execute_async(
                REGULAR_LOGIN_MUTATION, {"request": request.model_dump()}
            )
        ).regular_login
