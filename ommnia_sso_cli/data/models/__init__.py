from pydantic import BaseModel


class AuthConfigModel(BaseModel):
    email: str
    password: str


class ConfigModel(BaseModel):
    app_name: str
    graphql_endpoint_url: str
    client_private_key_path: str
    server_public_key_path: str
    auth: AuthConfigModel
