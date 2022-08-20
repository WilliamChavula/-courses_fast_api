from uuid import UUID
from typing import Optional

from pydantic import Field, BaseModel


class ModuleBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None


class ModuleResponse(ModuleBase):
    id: UUID

    class Config:
        orm_mode = True


class UpdateModuleBase(ModuleBase):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None

    class Config:
        orm_mode = True
