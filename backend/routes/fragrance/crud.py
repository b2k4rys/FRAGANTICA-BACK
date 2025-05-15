from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.db.models.fragrance import Fragrance, Company, FragranceType, Accord, AccordGroup
from backend.core.db.models.user import User as UserModel
from .schemas import CompanySchema, FragranceUpdate, FragranceRequestSchema, AccordRequestSchema, AccordGroupRequestSchema, AccordUpdateSchema
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, Response, Request
from ..auth.services import get_current_user

async def add_new_fragrance(session: AsyncSession, fragrance_data: FragranceRequestSchema, current_user: UserModel):
    new_fragrance = Fragrance(**fragrance_data.model_dump())
    session.add(new_fragrance)
    await session.commit()
    await session.refresh(new_fragrance)
    return new_fragrance

async def add_new_company(session: AsyncSession, company_data: CompanySchema, current_user: UserModel):

    new_company = Company(**company_data.model_dump())
    session.add(new_company)
    await session.commit()
    await session.refresh(new_company)
    return new_company

async def get_all_fragrances(session: AsyncSession, company_name: str | None = None, fragrance_type: FragranceType | None = None ):
    filters = []
    if company_name:
        company_name = company_name.strip()
        filters.append(Company.name.ilike(f"%{company_name}%"))
    if fragrance_type:
        filters.append(Fragrance.fragrance_type == fragrance_type)
    
    stmt = select(Fragrance).join(Company).filter(*filters).options(selectinload(Fragrance.company), selectinload(Fragrance.accords))
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


async def change_fragrance(
    fragrance_id: int,
    session: AsyncSession,
    updated_fragrance_data: FragranceUpdate
):
    stmt = select(Fragrance).options(selectinload(Fragrance.accords)).filter_by(id=fragrance_id)
    result = await session.execute(stmt)
    fragrance = result.scalar_one_or_none()

    if fragrance is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = updated_fragrance_data.model_dump(exclude_unset=True)


    for key, value in update_data.items():
        if key != "accords":
            setattr(fragrance, key, value)


    if "accords" in update_data:
        accord_ids = update_data["accords"] or []
        if accord_ids:
            result = await session.execute(select(Accord).where(Accord.id.in_(accord_ids)))
            accords = result.scalars().all()
            if len(accords) != len(accord_ids):
                raise HTTPException(status_code=400, detail="One or more accord_ids are invalid")
        else:
            accords = []

        fragrance.accords = accords

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



#  ACCORDS

async def get_accords(session: AsyncSession):
    stmt  = select(Accord)
    result  = await session.execute(stmt)
    accords = result.scalars().all()
    if not accords:
        raise HTTPException(status_code=404, detail="Not found")
    return accords

async def add_accord(accord: AccordRequestSchema, session: AsyncSession):
    new_accord = Accord(**accord.model_dump())
    session.add(new_accord)
    await session.commit()
    await session.refresh(new_accord)
    return new_accord

async def change_accord(accord_id: int, accord_update: AccordUpdateSchema, session: AsyncSession):
    result = await session.execute(select(Accord).filter_by(id=accord_id))
    accord = result.scalar_one_or_none()


    if accord is None:
        raise HTTPException(status_code=404, detail="Not found")

    update_data = accord_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(accord, key, value)

    await session.commit()
    await session.refresh(accord)
    return accord



async def add_accord_group(accord_group: AccordGroupRequestSchema, session: AsyncSession):
    new_accord_group = AccordGroup(**accord_group.model_dump())
    session.add(new_accord_group)
    await session.commit()
    await session.refresh(new_accord_group)
    return new_accord_group

