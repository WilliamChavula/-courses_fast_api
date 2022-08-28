from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.jwt_jose_provider import JoseJWTProvider
from auth.jwt_provider import JWTProvider
from core.exceptions import InvalidCredentialsException
from core.settings import Settings
from schemas.auth_schemas import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
jwt_provider: JWTProvider = JoseJWTProvider(
    algorithm=Settings.ALGORITHM, secret_key=Settings.SECRET_KEY
)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt_provider.encode(payload=to_encode)
    return encoded_jwt


def verify_token(token: str) -> Union[TokenData, None]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt_provider.decode(token=token)
        email: str = payload.get("user")
        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email)
        return token_data
    except InvalidCredentialsException:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme)) -> Union[TokenData, None]:
    return verify_token(token)
