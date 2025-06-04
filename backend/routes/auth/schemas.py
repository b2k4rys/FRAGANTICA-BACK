# src/schemas/user.py
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, EmailStr
from backend.core.db.models.user import Role

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Role = Role.USER

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def password_strength(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value

class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
class Token(BaseModel):
    access_token: str
    token_type: str


class UserEdit(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    ava: str | None= None
 

class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    role: Role
    ava: str
    model_config = ConfigDict(from_attributes=True)