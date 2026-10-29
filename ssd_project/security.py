from datetime import datetime, timedelta

from jose import jwt
from jose import JWTError

from passlib.context import CryptContext

from fastapi import HTTPException
from fastapi import Header
from fastapi import Depends

SECRET_KEY = "task_allotment_secret_key"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict):

    payload = data.copy()

    expire = (
        datetime.utcnow()
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload.update(
        {
            "exp": expire
        }
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )


def get_current_user(
        authorization: str = Header(...)
):

    token = authorization.replace(
        "Bearer ",
        ""
    )

    return decode_token(token)


def require_manager_or_admin(
        current_user=Depends(get_current_user)
):

    if current_user["role"] not in [
        "Admin",
        "Manager"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Access Denied"
        )

    return current_user


def require_admin(
        current_user=Depends(get_current_user)
):

    if current_user["role"] != "Admin":

        raise HTTPException(
            status_code=403,
            detail="Admin Access Required"
        )

    return current_user