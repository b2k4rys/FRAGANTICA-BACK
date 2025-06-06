from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.db.models.fragrance import Fragrance, Company, FragranceType, Note, NoteGroup, Review, Wishlist, FragranceNote, FragranceGender, Gender, NoteType, Season, FragranceSeason
from backend.core.db.models.user import User as UserModel
from backend.core.configs.config import settings
from .schemas import CompanySchema, FragranceUpdate, FragranceRequestSchema, NoteRequestSchema, NoteGroupRequestSchema, NoteUpdateSchema, ReviewCreateSchema, ReviewUpdateSchema, WishlistRequestSchema, Order
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, Response, Request, status, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
from fastapi_csrf_protect import CsrfProtect
import logging
from typing import Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def add_new_fragrance(
    session: AsyncSession, 
    fragrance_data: FragranceRequestSchema, 
):
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


async def add_new_company(
    session: AsyncSession, 
    company_data: CompanySchema
):

    new_company = Company(**company_data.model_dump())
    session.add(new_company)
    await session.commit()
    await session.refresh(new_company)
    return new_company

async def remove_company(
    company_id: int,
    session: AsyncSession
):
    if company_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company ID must be a positive integer"
        )
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
    page_size: int = Query(10, ge=1, le=100),
    min_price: int | None = Query(None, ge=0),
    max_price: int | None = Query(None, ge=0),
    order: Order = Order.asc
):
    filters = []
    if company_name:
        company_name = company_name.strip()
        filters.append(Company.name.ilike(f"%{company_name}%"))
    if fragrance_type:
        filters.append(Fragrance.fragrance_type == fragrance_type)
    if min_price is not None and max_price is not None and min_price >= max_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    if min_price is not None:
        filters.append(Fragrance.price >= min_price)
    if max_price is not None:
        filters.append(Fragrance.price <= max_price)

    if order == Order.desc:
        order = Fragrance.price.desc()
    else:
        order = Fragrance.price.asc()

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
            .order_by(order)
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
    """
    Update a fragrance's details and its associated notes.

    Args:
        fragrance_id (int): The ID of the fragrance to update.
        session (AsyncSession): The async database session.
        updated_fragrance_data (FragranceUpdate): Pydantic model with updated fragrance data.

    Returns:
        Fragrance: The updated fragrance object.

    Raises:
        HTTPException: If validation fails (400), fragrance not found (404), or a database error occurs (500).
    """
    if fragrance_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fragrance ID must be a positive integer"
        )
    stmt = select(Fragrance).options(selectinload(Fragrance.notes)).filter_by(id=fragrance_id)
    result = await session.execute(stmt)
    fragrance = result.scalar_one_or_none()

    if fragrance is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = updated_fragrance_data.model_dump(exclude_unset=True)


    for key, value in update_data.items():
        if key != "notes":
            setattr(fragrance, key, value)

    if "notes" in update_data:
        try:
            existing_notes = (await session.execute(select(FragranceNote).filter_by(fragrance_id=fragrance_id))).scalars().all()
            existing_note_ids = {note.note_id for note in existing_notes}

            update_note_ids = {note["note_id"] for note in update_data["notes"]}

            for n in update_data["notes"]:
                note_id = n.get("note_id")
                note_type_str = n.get("note_type")

                if note_id is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Note ID is required"
                    )
                
                note = await session.get(Note, note_id)
                if note is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Note with ID {note_id} does not exist"
                    )
                
                if note_type_str is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Note type is required"
                    )
                try:
                    note_type = NoteType(note_type_str)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid note type '{note_type_str}'. Must be one of {[e.value for e in NoteType]}"
                    )
                if note_id not in existing_note_ids:
                    note = FragranceNote(note_id=note_id, note_type=note_type_str, fragrance_id=fragrance_id)
                    session.add(note)
                else:
                    existing_note = (await session.execute(select(FragranceNote).filter_by(note_id=n["note_id"], fragrance_id=fragrance_id))).scalar_one()
                    existing_note.note_type = n["note_type"]
            

            for note_id in existing_note_ids:
                if note_id not in update_note_ids:
                    note_to_delete = (await session.execute(
                        select(FragranceNote).filter_by(note_id=note_id, fragrance_id=fragrance_id)
                    )).scalar_one()
                    await session.delete(note_to_delete)
            
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )


    await session.commit()
    await session.refresh(fragrance)
    return fragrance

async def get_fragrance_by_id(
    fragrance_id: int,
    session: AsyncSession,
) -> Dict:
    """
    Retrieve a fragrance by ID, including its reviews, notes, gender and season vote breakdown.

    Args:
        fragrance_id (int): The ID of the fragrance to retrieve.
        session (AsyncSession): The async database session.

    Returns:
        Dict: A dictionary containing the fragrance details and gender vote counts.

    Raises:
        HTTPException: If the fragrance is not found (404) or a database error occurs (500).
    """

    if fragrance_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fragrance ID must be a positive integer"
        )

    try:
        gender_counts_stmt = (
            select(
                FragranceGender.gender,
                func.count(FragranceGender.gender).label("vote_count")
            )
            .where(FragranceGender.fragrance_id == fragrance_id)
            .group_by(FragranceGender.gender)
        )
        gender_counts_result = await session.execute(gender_counts_stmt)
        gender_counts = {row.gender: row.vote_count for row in gender_counts_result}

        all_genders = {
            Gender.male: 0,
            Gender.mostly_male: 0,
            Gender.female: 0,
            Gender.mostly_female: 0,
            Gender.unisex: 0,
        }
        all_genders.update(gender_counts) 

        total_votes = sum(all_genders.values())

        season_counts_stmt =  (
            select(
            FragranceSeason.season,
            func.count(FragranceSeason.season).label("vote_count")
            )
            .where(FragranceSeason.fragrance_id == fragrance_id)
            .group_by(FragranceSeason.season)
        )
        season_count_result = await session.execute(season_counts_stmt)
        season_counts = {row.season: row.vote_count for row in season_count_result}

        all_seasons = {
            Season.winter: 0,
            Season.spring: 0,
            Season.summer: 0, 
            Season.fall: 0
        }
        all_seasons.update(season_counts)

        total_season_vote = sum(all_seasons.values())
        stmt = (
            select(Fragrance)
            .options(
                selectinload(Fragrance.fragrance_reviews),
                selectinload(Fragrance.notes)
            )
            .filter_by(id=fragrance_id)
        )
        result = await session.execute(stmt)
        fragrance = result.scalar_one_or_none()


        if fragrance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fragrance not found"
            )
        response = {
            "fragrance": fragrance,
            "gender_votes": {
                "total_votes": total_votes,
                "counts": {
                    "male": all_genders[Gender.male],
                    "mostly_male": all_genders[Gender.mostly_male],
                    "female": all_genders[Gender.female],
                    "mostly_female": all_genders[Gender.mostly_female],
                    "unisex": all_genders[Gender.unisex],
                },
                "percentages": (
                    {
                        "male": round((all_genders[Gender.male] / total_votes * 100), 2) if total_votes else 0,
                        "mostly_male": round((all_genders[Gender.mostly_male] / total_votes * 100), 2) if total_votes else 0,
                        "female": round((all_genders[Gender.female] / total_votes * 100), 2) if total_votes else 0,
                        "mostly_female": round((all_genders[Gender.mostly_female] / total_votes * 100), 2) if total_votes else 0,
                        "unisex": round((all_genders[Gender.unisex] / total_votes * 100), 2) if total_votes else 0,
                    }
                    if total_votes > 0
                    else None
                ),
            },
            "season_vote": {
                "total_votes": total_season_vote,
                "counts": {
                    "winter": all_seasons[Season.winter],
                    "spring": all_seasons[Season.spring],
                    "summer": all_seasons[Season.summer],
                    "fall": all_seasons[Season.fall],
                },
                "percentages": (
                    {
                        "winter": round((all_seasons[Season.winter] / total_season_vote * 100), 2) if total_season_vote else 0,
                        "spring": round((all_seasons[Season.spring] / total_season_vote * 100), 2) if total_season_vote else 0,
                        "summer": round((all_seasons[Season.summer] / total_season_vote * 100), 2) if total_season_vote else 0,
                        "fall": round((all_seasons[Season.fall] / total_season_vote * 100), 2) if total_season_vote else 0,

                    }
                    if total_season_vote > 0
                    else None
                ),

            }
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
    
async def delete_fragrance_by_id(
    fragrance_id: int, 
    session: AsyncSession
):
    if fragrance_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fragrance ID must be a positive integer"
        )
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

async def add_accord(
    note: NoteRequestSchema, 
    session: AsyncSession
):
    new_accord = Note(**note.model_dump())
    session.add(new_accord)
    await session.commit()
    await session.refresh(new_accord)
    return new_accord

async def change_accord(
    accord_id: int, 
    accord_update: NoteUpdateSchema, 
    session: AsyncSession
):
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

async def remove_note(
    note_id: int, 
    session: AsyncSession
):
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


async def add_accord_group(
    note_group: NoteGroupRequestSchema, 
    session: AsyncSession
):
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

async def add_review(
    review: ReviewCreateSchema, 
    request: Request, 
    current_user: UserModel, 
    session: AsyncSession, 
    csrf_protector: CsrfProtect
):
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


async def delete_review(
    review_id: int, 
    request: Request, 
    current_user: UserModel, 
    session: AsyncSession, 
    csrf_protector: CsrfProtect
):
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
    

async def edit_review(
    review_id: int, 
    review_update: ReviewUpdateSchema, 
    request: Request, 
    current_user: UserModel, 
    session: AsyncSession, 
    csrf_protector: CsrfProtect
):
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
async def add_to_or_edit_wishlist(
    wishlist: WishlistRequestSchema, 
    request: Request, 
    session: AsyncSession, 
    current_user: UserModel, 
    csrf_protector: CsrfProtect
):
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

async def remove_from_wishlist(
    wihlist_id: int,
    session: AsyncSession, 
    request: Request, 
    current_user: UserModel, 
    csrf_protector: CsrfProtect
):
    stmt = select(Wishlist).filter_by(id=wihlist_id, user_id=current_user.id)
    result = await session.execute(stmt)
    wishlist = result.scalar_one_or_none()

    if wishlist is None:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    await session.delete(wishlist)
    await session.commit()
    return Response(status_code=200, content="Item was deleted")



#                       ==== VOTING ==== 


#                       ==== GENDER ==== 
async def vote_for_gender(
    fragrance_id: int,
    gender: Gender,
    session: AsyncSession, 
    current_user: UserModel, 
):
    vote = (await session.execute(select(FragranceGender).filter_by(user_id=current_user.id, fragrance_id=fragrance_id))).scalar_one_or_none()
    if vote is not None:
        vote.gender = gender
        await session.commit()
        await session.refresh(vote)
        return vote
    
    new_gender_vote = FragranceGender(user_id=current_user.id, fragrance_id=fragrance_id, gender=gender)
    session.add(new_gender_vote)
    await session.commit()
    await session.refresh(new_gender_vote)
    return new_gender_vote

#                       ==== SEASON ==== 
async def vote_for_season(
    fragrance_id: int,
    season: Season,
    session: AsyncSession, 
    current_user: UserModel, 
): 
    fragrance = await session.get(Fragrance, fragrance_id)
    if fragrance is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Note with ID {fragrance_id} does not exist"
        )
    existing = (await session.execute(select(FragranceSeason).filter_by(fragrance_id=fragrance_id, user_id=current_user.id, season=season))).scalar_one_or_none()
    if existing:
        await session.delete(existing)
        await session.commit()
        return Response(status_code=200, content="item has been removed")
    
    try:
        new_season_vote = FragranceSeason(user_id=current_user.id, fragrance_id=fragrance_id, season=season)
        session.add(new_season_vote)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
    await session.commit()
    await session.refresh(new_season_vote)
    return new_season_vote
