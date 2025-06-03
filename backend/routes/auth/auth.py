from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..auth.schemas import User, UserCreate, Token, UserEdit, UserResponseSchema
from backend.core.db.models.user import User as UserModel
from backend.core.db.models.user import Role
from backend.core.configs.config import settings
from backend.core.db.session import get_async_session
from .services import hash_password, create_access_token, authenticate_user, require_role
from fastapi import UploadFile
import os
import shutil

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=User)
async def register_user(
    user: UserCreate,
    request: Request, 
    session: AsyncSession = Depends(get_async_session), 
    csrf_protect: CsrfProtect = Depends()
):
    if request.cookies.get(settings.cookie_name):
        await csrf_protect.validate_csrf(request)
    if (await session.execute(select(UserModel).filter(UserModel.username == user.username))).scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if (await session.execute(select(UserModel).filter(UserModel.email == user.email))).scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
    hashed_password = hash_password(user.password)
    db_user = UserModel(username=user.username, email=user.email, hashed_password=hashed_password, role=Role.USER)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.post("/login")
async def login_user(request: Request,response: Response, form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session), csrf_protect: CsrfProtect = Depends()):

    user = await authenticate_user(username=form_data.username, password=form_data.password, session=session)

    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    response.set_cookie(
        key=settings.cookie_name,
        value=access_token,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_access_token_expire_minutes * 60  
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):

    response.delete_cookie(
        key=settings.cookie_name,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
    )
    return {"message": "Logged out successfully"}
    

@router.get("/csrf-token")
async def get_csrf_token(response: Response, csrf_protect: CsrfProtect = Depends()):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,  
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return {"csrf_token": csrf_token}

@router.get("/me")
async def get_info_about_user(current_user: UserModel = Depends(require_role([Role.USER, Role.ADMIN]))):
    return UserResponseSchema.model_validate(current_user)

UPLOAD_DIR = "backend/static/images"

@router.patch("/me")
async def edit_user_info(user: UserEdit,  current_user: UserModel = Depends(require_role([Role.USER, Role.ADMIN])), session: AsyncSession = Depends(get_async_session)):
    if (await session.execute(select(UserModel).filter_by(username=user.username))).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if (await session.execute(select(UserModel).filter_by(email=user.email))).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
    user_db = (await session.execute(select(UserModel).filter_by(id=current_user.id))).scalar_one_or_none()
    user = user.model_dump(exclude_unset=True)


    for key, value in user.items():
        setattr(user_db, key, value)
    await session.commit()
    await session.refresh(user_db)
    return user_db


def post_ava(file: UploadFile | None = None):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    response = cloudinary.uploader.upload(f"/static/images/{file.filename}")
    return response.secure_url

    return {"filename": file.filename, "url": f"/static/images/{file.filename}"}

@router.post("/ava")
async def post_ava(file: UploadFile | None = None):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    response = cloudinary.uploader.upload(f"backend/static/images/{file.filename}")
    return response

    return {"filename": file.filename, "url": f"/static/images/{file.filename}"}
