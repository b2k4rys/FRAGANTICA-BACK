from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.db.models.fragrance import Fragrance, Company, FragranceType, Note, NoteGroup, Review, Wishlist, FragranceNote
from backend.core.db.models.user import User as UserModel
from backend.core.configs.config import settings
from .schemas import CompanySchema, FragranceUpdate, FragranceRequestSchema, NoteRequestSchema, NoteGroupRequestSchema, NoteUpdateSchema, ReviewCreateSchema, ReviewUpdateSchema, WishlistRequestSchema
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, Response, Request, status, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from ..auth.services import get_current_user
from pydantic import ValidationError, Field
from fastapi_csrf_protect import CsrfProtect
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def add_new_fragrance(session: AsyncSession, fragrance_data: FragranceRequestSchema, current_user: UserModel):
    try:
        new_fragrance = Fragrance(name=fragrance_data.name, company_id=fragrance_data.company_id, description=fragrance_data.description, fragrance_type=fragrance_data.fragrance_type, price=fragrance_data.price)
        session.add(new_fragrance)
        await session.flush()
        if fragrance_data.notes:
            for note in fragrance_data.notes:
                n = FragranceNote(fragrance_id=new_fragrance.id, note_id=note.note_id, note_type=note.note_type)
                session.add(n)
            await session.commit()
            await session.refresh(new_fragrance)
            return new_fragrance
    except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


async def add_new_company(session: AsyncSession, company_data: CompanySchema):

    new_company = Company(**company_data.model_dump())
    session.add(new_company)
    await session.commit()
    await session.refresh(new_company)
    return new_company

async def remove_company(company_id: int,session: AsyncSession):
    stmt = select(Company).filter_by(id=company_id)
    res = await session.execute(stmt)
    company =  res.scalar_one_or_none()
    
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    await session.delete(company)
    await session.commit()
    return Response(status_code=200, content="Item was deleted")


async def get_all_fragrances(
    session: AsyncSession,
    company_name: str | None = None, 
    fragrance_type: FragranceType | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    filters = []
    if company_name:
        company_name = company_name.strip()
        filters.append(Company.name.ilike(f"%{company_name}%"))
    if fragrance_type:
        filters.append(Fragrance.fragrance_type == fragrance_type)
    total_stmt = (
        select(func.count())
        .select_from(Fragrance)
        .join(Company)
        .filter(*filters)
    )

    total = await session.scalar(total_stmt)

    offset = (page - 1) * page_size
    stmt = (
            select(Fragrance)
            .join(Company)
            .filter(*filters)
            .options(
                selectinload(Fragrance.company),
                selectinload(Fragrance.notes)
            )
            .offset(offset)
            .limit(page_size)
        )
    
    result = await session.execute(stmt)
    fragrances = result.scalars().all()
    if not fragrances:
        raise HTTPException(status_code=404, detail="Not found")
    return {
    "total": total,
    "fragrances": fragrances
    }

async def get_all_companies(
    session: AsyncSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    offset = (page - 1) * page_size
    total_stmt = select(func.count()).select_from(Company)
    total = await session.scalar(total_stmt)

    stmt = select(Company).offset(offset).limit(page_size)
    result = await session.execute(stmt)
    companies = result.scalars().all()
    if not companies:
            raise HTTPException(status_code=404, detail="Not found")
    return {
    "total": total,
    "companies":companies
    }


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
            result = await session.execute(select(Note).where(Note.id.in_(accord_ids)))
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
    stmt = select(Fragrance).options(
        selectinload(Fragrance.fragrance_reviews),
        selectinload(Fragrance.notes)
    ).filter_by(id=fragrance_id)
    result = await session.execute(stmt)
    fragrance = result.scalar_one_or_none()
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

async def get_accords(
    session: AsyncSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    offset = (page - 1) * page_size
    stmt  = select(Note).offset(offset).limit(page_size)
    result  = await session.execute(stmt)
    accords = result.scalars().all()
    if not accords:
        raise HTTPException(status_code=404, detail="Not found")
    return accords

async def add_accord(note: NoteRequestSchema, session: AsyncSession):
    new_accord = Note(**note.model_dump())
    session.add(new_accord)
    await session.commit()
    await session.refresh(new_accord)
    return new_accord

async def change_accord(accord_id: int, accord_update: NoteUpdateSchema, session: AsyncSession):
    result = await session.execute(select(Note).filter_by(id=accord_id))
    accord = result.scalar_one_or_none()


    if accord is None:
        raise HTTPException(status_code=404, detail="Not found")

    update_data = accord_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(accord, key, value)

    await session.commit()
    await session.refresh(accord)
    return accord

async def remove_note(note_id: int, session: AsyncSession):
    stmt = select(Note).filter_by(id=note_id)
    result = await session.execute(stmt)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(code=404, detail="Item not found")
    try:
        await session.delete(note)
        await session.commit()
        return Response(status_code=200, content="Item was deleted successfully")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def add_accord_group(note_group: NoteGroupRequestSchema, session: AsyncSession):
    new_accord_group = NoteGroup(**note_group.model_dump())
    session.add(new_accord_group)
    await session.commit()
    await session.refresh(new_accord_group)
    return new_accord_group


#                       ==== REVIEWS ==== 

async def get_all_review(
    request: Request, 
    current_user: UserModel, 
    session: AsyncSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    total_stmt = select(func.count()).select_from(Review).filter_by(user_id=current_user.id)
    total = await session.scalar(total_stmt)
    offset =  (page - 1) * page_size
    stmt = select(Review).filter_by(user_id=current_user.id).offset(offset).limit(page_size)
    result = await session.execute(stmt)
    reviews = result.scalars().all()
    if reviews is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {
    "total_count": total,
    "reviews": reviews
    }

async def add_review(review: ReviewCreateSchema, request: Request, current_user: UserModel, session: AsyncSession, csrf_protector: CsrfProtect):
    if request.cookies.get(settings.cookie_name):
        csrf_protector.validate_csrf(request)
    
    try:
        db_review = Review(user_id=current_user.id, fragrance_id=review.fragrance_id, content=review.content, rating=review.rating)
        session.add(db_review)
        await session.commit()
        await session.refresh(db_review)
        return db_review
    except ValidationError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def delete_review(review_id: int, request: Request, current_user: UserModel, session: AsyncSession, csrf_protector: CsrfProtect):
    if request.cookies.get(settings.cookie_name):
        csrf_protector.validate_csrf(request)
    stmt = select(Review).filter_by(id = review_id, user_id=current_user.id)
    result = await session.execute(stmt)
    review = result.scalar_one_or_none()
    if review is None:
        raise HTTPException(status_code=404, detail="Item not found")
    try:
        await session.delete(review)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    

async def edit_review(review_id: int, review_update: ReviewUpdateSchema, request: Request, current_user: UserModel, session: AsyncSession, csrf_protector: CsrfProtect):
    if request.cookies.get(settings.cookie_name):
        csrf_protector.validate_csrf(request)
    stmt = select(Review).filter_by(id = review_id, user_id=current_user.id)
    result = await session.execute(stmt)
    review = result.scalar_one_or_none()
    if review is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = review_update.model_dump(exclude_unset=True)
   
    for key, value in update_data.items():
        setattr(review, key, value)
    await session.commit()
    await session.refresh(review)
    return review


#                       ==== WISHLIST ==== 
async def add_to_or_edit_wishlist(wishlist: WishlistRequestSchema, request: Request, session: AsyncSession, current_user: UserModel, csrf_protector: CsrfProtect):
    if request.cookies.get(settings.cookie_name):
        csrf_protector.validate_csrf(request)
    stmt = select(Wishlist).filter_by(user_id=current_user.id, fragrance_id=wishlist.fragrance_id)
    existing = await session.execute(stmt)
    existing = existing.scalar_one_or_none()

    if existing:
        existing.status = wishlist.status
        await session.commit()
        await session.refresh(existing)
        return existing

    wishlist_db = Wishlist(user_id=current_user.id, fragrance_id = wishlist.fragrance_id, status=wishlist.status)
    session.add(wishlist_db)
    await session.commit()
    await session.refresh(wishlist_db)
    return wishlist_db

async def remove_from_wishlist(wihlist_id: int,session: AsyncSession, request: Request, current_user: UserModel, csrf_protector: CsrfProtect):
    stmt = select(Wishlist).filter_by(id=wihlist_id, user_id=current_user.id)
    result = await session.execute(stmt)
    wishlist = result.scalar_one_or_none()

    if wishlist is None:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    await session.delete(wishlist)
    await session.commit()
    return Response(status_code=200, content="Item was deleted")