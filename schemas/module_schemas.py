"""Module schemas."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ModuleBase(BaseModel):
    """Module base schema."""

    title: str = Field(..., max_length=200)
    description: Optional[str] = None


class ModuleResponse(ModuleBase):
    """Module response schema."""

    id: UUID

    class Config:
        """Pydantic config."""

        orm_mode = True


class UpdateModuleBase(ModuleBase):
    """Update module base schema."""

    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None

    class Config:
        """Pydantic config."""

        orm_mode = True
