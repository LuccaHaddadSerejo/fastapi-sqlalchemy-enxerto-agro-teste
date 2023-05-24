from typing import Union, Any
from datetime import datetime
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db_setup import get_db
from fastapi.security import OAuth2PasswordBearer
from api.utils.jwt_utils import ALGORITHM, JWT_SECRET_KEY
from database.models.user_model import User
from jose import jwt
from pydantic import ValidationError
from schemas.token_schema import TokenPayload


reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT")


async def get_current_user(
    token: str = Depends(reuseable_oauth), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: Union[dict[str, Any], None] = (
        db.query(User).filter_by(id=token_data.sub).first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user
