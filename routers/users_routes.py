from typing import List, Union

from fastapi import APIRouter, Depends, Request, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from crud.users_crud import (
    db_create_user,
    db_insert_many,
    get_all_users,
    get_user_by_id,
    get_user_by_email,
    user_registration,
)
from models.user_models import UserModel
from schemas.auth_schemas import Token
from schemas.user_schemas import UserCreate, UserResponse

from auth.authenticate import create_access_token, logout
from auth.hashing import verify_password
from utils import Tags, get_db, verify_super_user

user_router = APIRouter(prefix="/user", tags=[Tags.users])


@user_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Create a user",
    dependencies=[Depends(verify_super_user)],
)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user_exists = get_user_by_email(db, user.email)

    if user_exists is not None:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    return await db_create_user(db, user)


@user_router.post(
    "/create_many",
    status_code=status.HTTP_201_CREATED,
    response_model=List[UserResponse],
    summary="Create users by passing a json Array of user objects",
    dependencies=[Depends(verify_super_user)],
)
async def create_users(users: List[UserCreate], db: Session = Depends(get_db)):
    res: List[UserModel] = await db_insert_many(db, users)
    return res


@user_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[UserResponse],
)
def get_users(
        db: Session = Depends(get_db),
        limit: int = Query(10, gt=0, le=100, description="Number of records to fetch"),
):
    users = get_all_users(db, limit)

    return users


@user_router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user: Union[None, UserResponse] = get_user_by_id(db=db, user_id=user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find user matching the credentials given",
        )

    return user


@user_router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
def login(
        req: OAuth2PasswordRequestForm = Depends(), database: Session = Depends(get_db)
) -> Token:
    user: Union[UserModel, None] = get_user_by_email(
        db=database, email_address=req.username
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
        )

    if not verify_password(req.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
        )

    access_token = create_access_token(data={"user": user.email})

    return Token(access_token=access_token)


@user_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(req: UserCreate, database: Session = Depends(get_db)):
    user = get_user_by_email(database, req.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    new_user = await user_registration(req, database)
    return new_user


@user_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(req: Request):
    token = req.headers.get("Authorization")

    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return logout(token)

