from fastapi import APIRouter, Depends
from .schemas import FragranceSchema, CompanySchema, FragranceUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from .crud import add_new_fragrance, add_new_company, get_all_fragrances, change_fragrance
from backend.core.db.session import get_async_session
from backend.core.db.models.fragrance import Fragrance

router = APIRouter(prefix="/fragrance", tags=['Fragrance routes'])

@router.post("/new-fragrance")
async def add_fragrance(fragrance_data: FragranceSchema, session: AsyncSession = Depends(get_async_session)):
    return await add_new_fragrance(session, fragrance_data)

@router.get("/all", response_model=List[FragranceSchema])
async def get_fragrances(session: AsyncSession = Depends(get_async_session)):
    return await get_all_fragrances(session)

@router.post("/new-company")
async def add_company(company_data: CompanySchema, session: AsyncSession = Depends(get_async_session)):
    return await add_new_company(session, company_data)


@router.patch("/edit-fragrance/{fragrance_id}")
async def edit_fragrance(fragrance_id: int, updated_fragrance_data: FragranceUpdate, session: AsyncSession = Depends(get_async_session)):

    return await change_fragrance(fragrance_id, session, updated_fragrance_data)
