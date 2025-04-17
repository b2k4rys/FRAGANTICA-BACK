from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.db.models.fragrance import Fragrance, Company
from .schemas import FragranceSchema, CompanySchema, ListFragranceResponseSchema
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

async def add_new_fragrance(session: AsyncSession, fragrance_data: FragranceSchema):
    new_fragrance = Fragrance(**fragrance_data.model_dump())
    session.add(new_fragrance)
    await session.commit()
    await session.refresh(new_fragrance)
    return new_fragrance

async def add_new_company(session: AsyncSession, company_data: CompanySchema):
    new_company = Company(**company_data.model_dump())
    session.add(new_company)
    await session.commit()
    await session.refresh(new_company)
    return new_company

async def get_all_fragrances(session: AsyncSession):
    stmt = select(Fragrance).options(selectinload(Fragrance.company))
    result = await session.execute(stmt)
    fragrances = result.scalars().all()
    if not fragrances:
        raise HTTPException(status_code=404, detail="No users found")
    return fragrances

async def change_fragrance( fragrance_id: int ,session: AsyncSession):
    stmt = select(Fragrance).filter_by(id=fragrance_id)
    result = await session.execute(stmt)
    fragrance = result.scalar_one_or_none()
    if fragrance is None:
        raise HTTPException(status_code=404, detail="Item not found")


