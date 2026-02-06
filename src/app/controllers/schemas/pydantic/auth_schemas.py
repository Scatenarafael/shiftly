from pydantic import BaseModel


class LoginRequestBody(BaseModel):
    email: str
    password: str


class UserIdResponse(BaseModel):
    user_id: str
