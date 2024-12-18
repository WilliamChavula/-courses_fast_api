from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.authenticate import get_current_user
from crud.users_crud import get_user_by_email
from models.session import SessionLocal
from models.user_models import UserModel
from schemas.auth_schemas import TokenData


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_super_user(db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    user: UserModel = get_user_by_email(
        db, email_address=current_user.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the right permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_super_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the right permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )
