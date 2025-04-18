from fastapi import APIRouter, Depends
from .schemas import FragranceSchema, CompanySchema, FragranceUpdate, FragranceRequestSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from .crud import add_new_fragrance, add_new_company, get_all_fragrances, change_fragrance, get_fragrance_by_id, delete_fragrance_by_id, get_all_companies
from backend.core.db.session import get_async_session
from backend.core.db.models.fragrance import Fragrance, FragranceType

router = APIRouter(prefix="/fragrance", tags=['Fragrance routes'])



# -- GET -- 
@router.get("/all", response_model=List[FragranceSchema])
async def get_fragrances(session: AsyncSession = Depends(get_async_session), company_name: str | None = None, fragrance_type: FragranceType | None = None):
    return await get_all_fragrances(session, company_name, fragrance_type)

@router.get("/all/{fragrance_id}")
async def get_fragrance(fragrance_id: int,session: AsyncSession = Depends(get_async_session)):
    return await get_fragrance_by_id(fragrance_id, session)

@router.get("/company/all")
async def get_all_company(session: AsyncSession  = Depends(get_async_session)):
    return await get_all_companies(session)
# -- POST -- 
@router.post("/new-fragrance")
async def add_fragrance(fragrance_data: FragranceRequestSchema, session: AsyncSession = Depends(get_async_session)):
    return await add_new_fragrance(session, fragrance_data)


@router.post("/new-company")
async def add_company(company_data: CompanySchema, session: AsyncSession = Depends(get_async_session)):
    return await add_new_company(session, company_data)


# -- PATCH -- 
@router.patch("/all/{fragrance_id}")
async def edit_fragrance(fragrance_id: int, updated_fragrance_data: FragranceUpdate, session: AsyncSession = Depends(get_async_session)):
    return await change_fragrance(fragrance_id, session, updated_fragrance_data)


# -- DELETE -- 
@router.delete("/all/{fragrance_id}")
async def delete_fragrance(fragrance_id: int,session: AsyncSession = Depends(get_async_session)):
    return await delete_fragrance_by_id(fragrance_id, session)