from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..auth.schemas import User, UserCreate, Token
from backend.core.db.models.user import User as UserModel
from backend.core.configs.config import settings
from backend.core.db.session import get_async_session
from ..auth.cruds import hash_password, create_access_token, authenticate_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=User)
async def register_user(username: str, password:str,email: str, session: AsyncSession = Depends(get_async_session)):
    if (await session.execute(select(UserModel).filter(UserModel.username == username))).scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if (await session.execute(select(UserModel).filter(UserModel.email == email))).scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email alreadt taken")
    
    hashed_password = hash_password(password)
    db_user = UserModel(username=username, email=email, hashed_password=hashed_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session)):
    user = await authenticate_user(username=form_data.username, password=form_data.password, session=session)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


    