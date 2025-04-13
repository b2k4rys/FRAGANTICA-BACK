from fastapi import APIRouter, Depends
from .schemas import FragranceSchema
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import add_new_fragrance
from backend.core.db.session import get_async_session


router = APIRouter(prefix="/fragrance", tags=['Fragrance routes'])

@router.post("/new-fragrance")
async def add_fragrance(fragrance_data: FragranceSchema, session: AsyncSession = Depends(get_async_session)):
    return await add_new_fragrance(session, fragrance_data)


@router.post("/new-company")
async def add_new_company():
    pass