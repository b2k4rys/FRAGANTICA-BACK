from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.db.models.fragrance import Fragrance, Company
from .schemas import FragranceSchema, CompanySchema, ListFragranceResponseSchema, FragranceUpdate, FragranceRequestSchema
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, Response

async def add_new_fragrance(session: AsyncSession, fragrance_data: FragranceRequestSchema):
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

async def get_all_fragrances(session: AsyncSession, company_name: str | None = None):

    if company_name:
        stmt = (
            select(Fragrance)
            .join(Fragrance.company)
            .filter(Company.name.ilike(f"%{company_name}%"))
            .options(selectinload(Fragrance.company))
        )
    else:
        stmt = select(Fragrance).options(selectinload(Fragrance.company))
    result = await session.execute(stmt)
    fragrances = result.scalars().all()
    if not fragrances:
        raise HTTPException(status_code=404, detail="Not found")
    return fragrances

async def get_all_companies(session: AsyncSession):
    stmt = select(Company)
    result = await session.execute(stmt)
    companies = result.scalars().all()
    if not companies:
            raise HTTPException(status_code=404, detail="Not found")
    return companies

async def change_fragrance( fragrance_id: int, session: AsyncSession, updated_fragrance_data:FragranceUpdate):
    db_item = select(Fragrance).filter_by(id=fragrance_id)
    
    result = await session.execute(db_item)
    fragrance = result.scalar_one()


    if fragrance is None:
        raise HTTPException(status_code=404, detail="Item not found")
  
    update_item = updated_fragrance_data.model_dump(exclude_unset=True)
 
    
    for key, value in update_item.items():
        setattr(fragrance, key, value)

    await session.commit()
    await session.refresh(fragrance)
    return fragrance

async def get_fragrance_by_id(fragrance_id: int, session: AsyncSession):
    stmt = select(Fragrance).filter_by(id=fragrance_id)
    result = await session.execute(stmt)
    fragrance = result.scalar_one()
    if fragrance is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return fragrance


async def delete_fragrance_by_id(fragrance_id: int, session: AsyncSession):
    stmt = select(Fragrance).filter_by(id=fragrance_id)
    result = await session.execute(stmt)
    fragrance = result.scalar_one()
    if fragrance is None:
        raise HTTPException(status_code=404, detail="Item not found")
    await session.delete(fragrance)
    await session.commit()
    return Response(status_code=200, content="Item was deleted")
