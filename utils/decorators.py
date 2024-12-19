from typing import Callable

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from crud.users_crud import get_user_by_email
from models.user_models import UserModel
from schemas.auth_schemas import TokenData


def check_super_user(db: Session, current_user: TokenData):
    def get_user(function: Callable):
        def path_operation_function(*args, **kwargs):
            user: UserModel = get_user_by_email(db, email_address=current_user.email)

            if not user.is_super_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have the right permissions",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            function(*args, **kwargs)

        return path_operation_function

    return get_user
