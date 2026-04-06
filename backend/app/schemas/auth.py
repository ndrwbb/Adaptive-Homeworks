from typing import Literal

from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=6)
    role: Literal["student", "teacher"]
    full_name: str = Field(min_length=2, max_length=255)


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

