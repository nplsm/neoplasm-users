from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, validator


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class TokensPayload(BaseModel):
    error: Optional[str]
    tokens: Optional[Tokens]


class UserRegister(BaseModel):
    email: EmailStr
    password1: str
    password2: str
    registration_datetime: datetime = datetime.utcnow()

    @validator("password1")
    def validate_password_length(cls, password1: str) -> str:
        if len(password1) < 12:
            raise ValueError("Password must be at least 12 characters long")
        return password1

    @validator("password2")
    def validate_passwords_match(cls, password2: str, values: dict) -> str:
        if "password1" in values and password2 != values["password1"]:
            raise ValueError("Passwords must match")
        return password2


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserSave(BaseModel):
    email: EmailStr
    hashed_password: str
    registration_datetime: datetime


class User(UserSave):
    id: ObjectId = Field(alias="_id")
    hashed_refresh_token: Optional[str]

    class Config:
        arbitrary_types_allowed = True


class UserPayload(BaseModel):
    error: Optional[str]
    user: Optional[User]
    tokens: Optional[Tokens]
