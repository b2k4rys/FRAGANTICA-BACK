from datetime import datetime, timedelta
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.core.db.models.user import User as UserModel
from backend.core.db.models.user import Role
from backend.core.configs.config import settings
from backend.core.db.session import get_async_session


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT token generation
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def authenticate_user(username: str, password: str, session: AsyncSession) -> Optional[UserModel]:
    user = await session.execute(select(UserModel).filter(UserModel.username == username))
    user = user.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_async_session)) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token: 
        token_source = token
    else:
        token_source = request.cookies.get(settings.cookie_name)
        if not token_source:
            raise credentials_exception
    try:
        payload  = jwt.decode(token_source, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await session.execute(select(UserModel).filter(UserModel.username == username))
    user = user.scalars().first()
    if user is None:
        raise credentials_exception
    return user


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def require_role(required_roles: List[Role]):
    async def role_checker(
        current_user: UserModel = Depends(get_current_user)
    ) -> UserModel:
        

        if current_user.role not in required_roles:
            allowed_roles = ", ".join(role.value for role in required_roles)
            raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Role must be one of: {allowed_roles}"
                        )
        return current_user
    return role_checker
