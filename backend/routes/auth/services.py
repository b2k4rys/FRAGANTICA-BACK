from datetime import datetime, timedelta
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.core.db.models.user import User as UserModel
from backend.core.db.models.user import Role
from backend.core.configs.config import settings
from backend.core.db.session import get_async_session
import os
import shutil
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

UPLOAD_DIR = "backend/static/images"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT token generation
def create_access_token(data: dict, expire_time: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expire_time:
        expire = datetime.utcnow() + expire_time
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode ,key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

async def authenticate_user(username: str, password: str, session: AsyncSession) -> Optional[UserModel]:
    user = await session.execute(select(UserModel).filter(UserModel.username == username))
    user = user.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_async_session)):
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
        payload = jwt.decode(token_source, key=settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await session.execute(select(UserModel).filter(UserModel.username == username))
    user = user.scalars().first()
    if user is None:
        raise credentials_exception
    return user



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


def post_ava(file: UploadFile | None = None):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    
    response = cloudinary.uploader.upload(f"backend/static/images/{file.filename}")
    url = response['secure_url']

    if url is None: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='problem with ava upload')
    
    if os.path.exists(file_path):
        os.remove(file_path)
    return url