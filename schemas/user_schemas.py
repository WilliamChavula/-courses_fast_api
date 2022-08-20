from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Union


class BaseUser(BaseModel):
    first_name: str = Field(..., description='First Name')
    last_name: str = Field(..., description='Last Name')
    email: EmailStr
    job_title: str = Field(..., description="Job title")
    is_super_user: bool = Field(default=False, description="Is Super User")

    class Config:
        validate_assignment = True
        anystr_strip_whitespace = True


class UserCreate(BaseUser):
    id: str = Field(..., min_length=30)
    password: str = Field(..., min_length=6)

    class Config:
        validate_assignment = True
        anystr_strip_whitespace = True


class UserResponse(BaseUser):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: Union[EmailStr, str]
    password: str
