from fastapi import APIRouter, Depends, Request, Query
from .schemas import FragranceSchema, CompanySchema, FragranceUpdate, FragranceRequestSchema, NoteRequestSchema, NoteGroupRequestSchema, NoteUpdateSchema, ReviewCreateSchema, ReviewUpdateSchema, WishlistRequestSchema, FragrancePaginatesResponseSchema
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.core.db.session import get_async_session
from backend.core.db.models.fragrance import FragranceType
from backend.core.db.models.user import User as UserModel
from backend.core.db.models.user import Role
from ..auth.services import get_current_user, require_role
from ..fragrance import crud
from fastapi_csrf_protect import CsrfProtect
from fastapi_pagination import Page, paginate

router = APIRouter(prefix="/fragrance", tags=['Fragrance routes'])


#                       ==== FRAGRANCE ==== 
@router.get("/all", response_model=FragrancePaginatesResponseSchema) 
async def get_fragrances(
    session: AsyncSession = Depends(get_async_session), 
    company_name: str | None = None, 
    fragrance_type: FragranceType | None = None,  
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    min_price: int | None = Query(None, ge=0),
    max_price: int | None = Query(None, ge=0),
):
    return await crud.get_all_fragrances(session, company_name, fragrance_type, page, page_size, min_price, max_price)

@router.get("/all/{fragrance_id}")
async def get_fragrance(
    fragrance_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    return await crud.get_fragrance_by_id(fragrance_id, session)

@router.post("/new-fragrance")
async def add_fragrance(
    fragrance_data: FragranceRequestSchema, 
    session: AsyncSession = Depends(get_async_session), 
    current_user: UserModel = Depends(require_role([Role.ADMIN]))
):
    return await crud.add_new_fragrance(session, fragrance_data)

@router.patch("/all/{fragrance_id}")
async def edit_fragrance(
    fragrance_id: int, 
    updated_fragrance_data: FragranceUpdate, 
    session: AsyncSession = Depends(get_async_session), 
    current_user: UserModel = Depends(require_role([Role.ADMIN]))
):
    return await crud.change_fragrance(fragrance_id, session, updated_fragrance_data)

@router.delete("/all/{fragrance_id}")
async def delete_fragrance(
    fragrance_id: int,
    session: AsyncSession = Depends(get_async_session), 
    current_user: UserModel = Depends(require_role([Role.ADMIN]))
):
    return await crud.delete_fragrance_by_id(fragrance_id, session)


#                       ==== COMPANY ==== 
@router.get("/company/all")
async def get_all_company(
    session: AsyncSession  = Depends(get_async_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    return await crud.get_all_companies(session, page, page_size)

@router.post("/new-company")
async def add_company( 
    request: Request,
    company_data: CompanySchema, 
    session: AsyncSession = Depends(get_async_session), 
    current_user: UserModel = Depends(require_role([Role.ADMIN]))
):
    return await crud.add_new_company(session, company_data)

@router.delete("/company/{company_id}")
async def remove_company(
    company_id: int, 
    session: AsyncSession = Depends(get_async_session), 
    current_user: UserModel = Depends(require_role([Role.ADMIN]))
):
    return await crud.remove_company(company_id, session)

#                       ==== ACCCORDS ==== 
@router.get("/accords")
async def get_accords(
    session: AsyncSession = Depends(get_async_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    return await crud.get_accords(session, page, page_size)

@router.post("/accords/")
async def add_accord(
    accord: NoteRequestSchema, 
    session: AsyncSession = Depends(get_async_session), 
    current_user: UserModel = Depends(require_role([Role.ADMIN]))
):
    return await crud.add_accord(accord, session)

@router.patch("/accords/{accord_id}")
async def update_accord(
    accord_id: int, 
    accord_update: NoteUpdateSchema, 
    session: AsyncSession = Depends(get_async_session), 
    current_user: UserModel = Depends(require_role([Role.ADMIN]))
):
    return await crud.change_accord(accord_id, accord_update, session)

@router.delete("/accords/{accord_id}")
async def remove_note(
    note_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    return await crud.remove_note(note_id, session)

@router.post("/accords/group")
async def add_accord_group(
    accord_group: NoteGroupRequestSchema,
    session: AsyncSession = Depends(get_async_session), 
    current_user: UserModel = Depends(require_role([Role.ADMIN]))
):
    return await crud.add_accord_group(accord_group, session)


#                       ==== REVIEWS ==== 
@router.get("/reviews")
async def get_all_review(
    request: Request, 
    current_user: UserModel = Depends(require_role([Role.ADMIN, Role.USER])), 
    session: AsyncSession = Depends(get_async_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    return await crud.get_all_review(request, current_user, session, page, page_size)

@router.post("/reviews")
async def add_review(
    review: ReviewCreateSchema,
    request: Request, 
    current_user: UserModel = Depends(require_role([Role.ADMIN, Role.USER])), 
    session: AsyncSession = Depends(get_async_session), 
    csrf_protector: CsrfProtect = Depends() 
):
    return await crud.add_review(review, request, current_user, session, csrf_protector)

@router.patch("/reviews/{review_id}")
async def edit_review(
    review_id: int,
    review_update: ReviewUpdateSchema, 
    request: Request, 
    current_user: UserModel = Depends(require_role([Role.ADMIN, Role.USER])), 
    session: AsyncSession = Depends(get_async_session), 
    csrf_protector: CsrfProtect = Depends()
):
    return await crud.edit_review(review_id, review_update, request, current_user, session, csrf_protector)

@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: int, 
    request: Request, 
    current_user: UserModel = Depends(require_role([Role.ADMIN, Role.USER])), 
    session: AsyncSession = Depends(get_async_session), 
    csrf_protector: CsrfProtect = Depends()
):
    return await crud.delete_review(review_id ,request, current_user, session, csrf_protector)


#                       ==== WISHLIST ==== 


@router.post("/wishlist")
async def add_to_or_edit_wishlist(
    wishlist: WishlistRequestSchema, 
    request: Request, 
    session: AsyncSession = Depends(get_async_session), 
    current_user: UserModel = Depends(require_role([Role.USER, Role.ADMIN])), 
    csrf_protector: CsrfProtect = Depends()
):
    return await crud.add_to_or_edit_wishlist(wishlist, request, session, current_user, csrf_protector)

@router.delete("/wishlist/{wishlist_id}")
async def remove_review(
    wishlist_id: int,  
    session: AsyncSession = Depends(get_async_session), 
    current_user: UserModel = Depends(require_role([Role.USER, Role.ADMIN])), 
    csrf_protector: CsrfProtect = Depends()
):
    await crud.remove_from_wishlist(wishlist_id,session , current_user, csrf_protector)