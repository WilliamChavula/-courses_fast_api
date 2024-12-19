from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.jwt_jose_provider import JoseJWTProvider
from auth.jwt_provider import JWTProtocol
from core.exceptions import InvalidCredentialsException
from core.settings import Settings
from schemas.auth_schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
jwt_provider: JWTProtocol = JoseJWTProvider(
    algorithm=Settings.ALGORITHM, secret_key=Settings.SECRET_KEY
)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
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

        expire_time_string = payload.get("exp")

        if expire_time_string is None:
            raise credentials_exception

        parsed_expire = datetime.fromtimestamp(int(expire_time_string), tz=timezone.utc)

        if parsed_expire < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please login",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = TokenData(email=email)
        return token_data
    except InvalidCredentialsException:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme)) -> Union[TokenData, None]:
    return verify_token(token)


def logout(token: str) -> str:
    try:
        token = token.split(" ")[1]
        payload = jwt_provider.decode(token=token)
        expire_time_string = payload.get("exp")

        if expire_time_string is None:
            raise HTTPException(
                status_code=status.HttpStatus.BAD_REQUEST,
                detail="Failed to perform requested action",
                headers={"WWW-Authenticate": "Bearer"},
            )

        expire_token = datetime.fromtimestamp(
            int(expire_time_string), tz=timezone.utc
        ) - timedelta(hours=24)

        payload.update({"exp": expire_token})
        encoded_jwt = jwt_provider.encode(payload=payload)
        return encoded_jwt

    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to perform requested action",
            headers={"WWW-Authenticate": "Bearer"},
        )
