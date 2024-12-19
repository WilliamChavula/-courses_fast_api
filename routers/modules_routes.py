from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from crud.modules_crud import (
    db_read_all_modules,
    db_read_module_by_id,
    db_update_module,
    db_create_module,
    delete_module_by_id,
)
from models.module_models import ModuleModel
from schemas import ModuleResponse, UpdateModuleBase
from schemas.module_schemas import ModuleBase
from utils import Tags, get_db, verify_super_user

module_router = APIRouter(prefix="/modules", tags=[Tags.modules])


@module_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[ModuleResponse],
    tags=[Tags.modules],
    summary="Query Course modules",
)
def get_modules(db: Session = Depends(get_db), limit: int = Query(10, gt=0, le=100)):
    return db_read_all_modules(db, limit)


@module_router.get(
    "/{module_id}",
    status_code=status.HTTP_200_OK,
    response_model=ModuleResponse,
    tags=[Tags.modules],
    summary="Query Course module by ID",
)
def get_module_by_id(module_id: str, db: Session = Depends(get_db)):
    module: Union[ModuleModel, None] = db_read_module_by_id(db=db, module_id=module_id)

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id: {module_id} does not exist",
        )

    return module


@module_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ModuleResponse,
    dependencies=[Depends(verify_super_user)],
)
async def create_module(module: ModuleBase, db: Session = Depends(get_db)):
    created = await db_create_module(db, module)
    return created


@module_router.put(
    "/{module_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ModuleResponse,
    dependencies=[Depends(verify_super_user)],
    tags=[Tags.modules],
    summary="Update Course module by ID",
)
async def update_module(
    *, db: Session = Depends(get_db), module_id: str, content: UpdateModuleBase
):
    module: Union[ModuleModel, None] = await db_update_module(db, module_id, content)

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find module with ID: {module_id}",
        )

    return module


@module_router.delete(
    "/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_super_user)],
)
async def delete_module(module_id: str, db: Session = Depends(get_db)):
    module = get_module_by_id(module_id, db)

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find module with ID: {module_id}",
        )

    await delete_module_by_id(db, module_id)
