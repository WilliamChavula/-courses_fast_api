from datetime import datetime
from typing import Union

from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")
    email: EmailStr
    job_title: str = Field(..., description="Job title")
    is_super_user: bool = Field(default=False, description="Is Super User")

    class Config:
        validate_assignment = True
        anystr_strip_whitespace = True


class UserCreate(BaseUser):
    password: str = Field(..., min_length=6, max_length=30)

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
