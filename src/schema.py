from pydantic import BaseModel

class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str


class LoginSchema(BaseModel):
    username: str
    password: str