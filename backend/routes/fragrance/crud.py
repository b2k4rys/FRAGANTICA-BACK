from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.db.models.fragrance import Fragrance
from .schemas import FragranceSchema

async def add_new_fragrance(session: AsyncSession, fragrance_data: FragranceSchema):
    new_fragrance = Fragrance(**fragrance_data.model_dump())
    session.add(new_fragrance)
    await session.commit()
    await session.refresh(new_fragrance)
    return new_fragrance
