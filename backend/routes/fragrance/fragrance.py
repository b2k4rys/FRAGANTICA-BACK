from fastapi import APIRouter, Depends, Request
from .schemas import FragranceSchema, CompanySchema, FragranceUpdate, FragranceRequestSchema, AccordRequestSchema, AccordGroupRequestSchema, AccordUpdateSchema, ReviewCreateSchema, ReviewUpdateSchema
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .crud import add_new_fragrance, add_new_company, get_all_fragrances, change_fragrance, get_fragrance_by_id, delete_fragrance_by_id, get_all_companies
from backend.core.db.session import get_async_session
from backend.core.db.models.fragrance import FragranceType
from backend.core.db.models.user import User as UserModel
from backend.core.db.models.user import Role
from ..auth.services import get_current_user, require_role
from ..fragrance import crud
from fastapi_csrf_protect import CsrfProtect
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
async def add_fragrance(fragrance_data: FragranceRequestSchema, session: AsyncSession = Depends(get_async_session), current_user: UserModel = Depends(require_role([Role.ADMIN]))):
    return await add_new_fragrance(session, fragrance_data, current_user)


@router.post("/new-company")
async def add_company( request: Request,company_data: CompanySchema, session: AsyncSession = Depends(get_async_session), current_user: UserModel = Depends(require_role([Role.ADMIN]))):
    return await add_new_company(session, company_data)


# -- PATCH -- 
@router.patch("/all/{fragrance_id}")
async def edit_fragrance(fragrance_id: int, updated_fragrance_data: FragranceUpdate, session: AsyncSession = Depends(get_async_session), current_user: UserModel = Depends(require_role([Role.ADMIN]))):
    return await change_fragrance(fragrance_id, session, updated_fragrance_data)


# -- DELETE -- 
@router.delete("/all/{fragrance_id}")
async def delete_fragrance(fragrance_id: int,session: AsyncSession = Depends(get_async_session), current_user: UserModel = Depends(require_role([Role.ADMIN]))):
    return await delete_fragrance_by_id(fragrance_id, session)




#                       ==== ACCCORDS ==== 
@router.get("/accords")
async def get_accords(session: AsyncSession = Depends(get_async_session)):
    return await crud.get_accords(session)

@router.post("/accords/")
async def add_accord(accord: AccordRequestSchema, session: AsyncSession = Depends(get_async_session), current_user: UserModel = Depends(require_role([Role.ADMIN]))):
    return await crud.add_accord(accord, session)

@router.patch("/accords/{accord_id}")
async def update_accord(accord_id: int, accord_update: AccordUpdateSchema, session: AsyncSession = Depends(get_async_session), current_user: UserModel = Depends(require_role([Role.ADMIN]))):
    return await crud.change_accord(accord_id, accord_update, session)

@router.post("/accords/group")
async def add_accord_group(accord_group: AccordGroupRequestSchema, session: AsyncSession = Depends(get_async_session), current_user: UserModel = Depends(require_role([Role.ADMIN]))):
    return await crud.add_accord_group(accord_group, session)




#                       ==== REVIEWS ==== 
@router.post("/reviews")
async def add_review(review: ReviewCreateSchema, request: Request, current_user: UserModel = Depends(require_role([Role.ADMIN, Role.USER])), session: AsyncSession = Depends(get_async_session), csrf_protector: CsrfProtect = Depends() ):
    return await crud.add_review(review, request, current_user, session, csrf_protector)

@router.patch("/reviews/{review_id}")
async def edit_review(review_id: int, review_update: ReviewUpdateSchema, request: Request, current_user: UserModel = Depends(require_role([Role.ADMIN, Role.USER])), session: AsyncSession = Depends(get_async_session), csrf_protector: CsrfProtect = Depends()):
    return await crud.edit_review(review_id, review_update, request, current_user, session, csrf_protector)

@router.delete("/reviews/{review_id}")
async def delete_review(review_id: int, request: Request, current_user: UserModel = Depends(require_role([Role.ADMIN, Role.USER])), session: AsyncSession = Depends(get_async_session), csrf_protector: CsrfProtect = Depends()):
    return await crud.delete_review(review_id ,request, current_user, session, csrf_protector)
