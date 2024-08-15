from typing import Literal
from pydantic.alias_generators import to_camel
from pydantic import BaseModel, ConfigDict
from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class UserSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    uid: int
    status: UserStatus
    name: str


class RegularUserSchema(UserSchema):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    typename: Literal["RegularUserSchema"] = "RegularUserSchema"
    email: str
    password_hash: str
