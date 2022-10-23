from fastapi import APIRouter, Depends

from schemas.companies_members import Invite, ResponseMessage, MyInvites, AcceptDecline, CompanyMemberModel
from schemas.company import Companies
from db.models import company_members as DBCompany_members, company as DBCompany
from repositories.companies_members import CompanyMemberCRUD
from repositories.company import CompanyCRUD
from utils.exceptions import CustomError
from utils.permissions import Permissions
from endpoints.auth import read_users_me

router = APIRouter()



@router.post("/invite_member", response_model=ResponseMessage, status_code=201)
async def invite_member(invite: Invite, user = Depends(read_users_me)) -> ResponseMessage:
    crud = CompanyCRUD(db_company=DBCompany)
    company = await crud.get_by_id(id=invite.company_id)
    await Permissions(user=user).permission_validator_for_company(id=id, company=company)
    crud = CompanyMemberCRUD(db_company_members=DBCompany_members)
    return await crud.invite_member(invite=invite)


@router.get("/my_invites", response_model=MyInvites)
async def get_companies_list(page: int = 1, limit: int = 10, user = Depends(read_users_me)) -> MyInvites:
    await Permissions(user=user).validate_token()
    crud = CompanyMemberCRUD(db_company_members=DBCompany_members)
    return await crud.my_invites(user_id=user.id, page=page, limit=limit)


@router.post("/accept_invite", response_model=ResponseMessage)
async def accept_invite(accept: AcceptDecline, user = Depends(read_users_me)) -> ResponseMessage:
    crud = CompanyMemberCRUD(db_company_members=DBCompany_members)
    member = await crud.get_by_id(id=accept.id)
    await Permissions(user=user).permission_validator_for_member(member=member)
    return await crud.accept_invite(id=accept.id)


@router.post("/decline_invite", response_model=ResponseMessage)
async def decline_invite(decline: AcceptDecline, user = Depends(read_users_me)) -> ResponseMessage:
    crud = CompanyMemberCRUD(db_company_members=DBCompany_members)
    member = await crud.get_by_id(id=decline.id)
    await Permissions(user=user).permission_validator_for_member(member=member)
    return await crud.decline_invite(id=decline.id)


@router.post("/ignore_invite", response_model=ResponseMessage)
async def ignore_invite(decline: AcceptDecline, user = Depends(read_users_me)) -> ResponseMessage:
    """ To stop spaming invites from company user can ignore it """

    crud = CompanyMemberCRUD(db_company_members=DBCompany_members)
    member = await crud.get_by_id(id=decline.id)
    await Permissions(user=user).permission_validator_for_member(member=member)
    return await crud.ignore_invite(id=decline.id)


@router.get("/{id}/users")
async def get_users_list(id: int = id, user = Depends(read_users_me), page: int = 1, limit: int = 10):
    await Permissions(user=user).validate_token()
    crud = CompanyMemberCRUD(db_company_members=DBCompany_members)
    return await crud.users_in_company(user_id=user.id, company_id=id, page=page, limit=limit)