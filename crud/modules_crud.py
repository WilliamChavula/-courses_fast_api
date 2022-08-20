from typing import Union, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas import ModuleBase, UpdateModuleBase
from models import ModuleModel


async def db_create_module(db: Session, mod: ModuleBase):
    module_item = ModuleModel(**mod.dict())
    db.add(module_item)
    db.commit()
    db.refresh(module_item)

    return module_item


def db_read_all_modules(db: Session, limit: int) -> List[ModuleModel]:
    return db.scalars(
        select(ModuleModel)
    ).fetchmany(size=limit)


def db_read_module_by_id(db: Session, module_id: str) -> Union[ModuleModel, None]:
    module, = db.execute(
        select(ModuleModel).where(ModuleModel.id == module_id)
    ).one_or_none()

    return module


async def db_update_module(
    db: Session, module_id: str,  content: UpdateModuleBase
) -> Union[ModuleModel, None]:
    module = db.scalar(
        select(ModuleModel).where(ModuleModel.id == module_id)
    )

    if module is None:
        return

    for key, val in vars(content).items():
        setattr(module, key, val) if val else None
    db.add(module)
    db.commit()

    return module


# DELETE QUERIES

async def delete_module_by_id(db: Session, module_id: str) -> Union[None, ModuleModel]:
    module: ModuleModel = (
        db.query(ModuleModel).filter(ModuleModel.id == module_id).one_or_none()
    )

    if module is None:
        return None

    db.delete(module)
    db.commit()

    return module
