from fastapi import APIRouter, Depends

from schemas import companies_members as schemas_cm
from repositories.companies_members import CompanyMemberCRUD
from repositories.company import CompanyCRUD
from utils.permissions import Permissions
from endpoints.auth import read_users_me
from db.connection import database as db

router = APIRouter()



@router.post("/invite_member", response_model=schemas_cm.ResponseMessage, status_code=201)
async def invite_member(invite: schemas_cm.Invite, user = Depends(read_users_me)) -> schemas_cm.ResponseMessage:
    company = await CompanyCRUD(db=db).get_by_id(id=invite.company_id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    crud = CompanyMemberCRUD(db=db)
    return await crud.invite_member(invite=invite)


@router.get("/my_invites", response_model=schemas_cm.MyInvites)
async def get_companies_list(page: int = 1, limit: int = 10, user = Depends(read_users_me)) -> schemas_cm.MyInvites:
    await Permissions(user=user).validate_token()
    crud = CompanyMemberCRUD(db=db)
    return await crud.my_invites(user_id=user.id, page=page, limit=limit)


@router.post("/accept_invite", response_model=schemas_cm.ResponseMessage)
async def accept_invite(accept: schemas_cm.AcceptDecline, user = Depends(read_users_me)) -> schemas_cm.ResponseMessage:
    crud = CompanyMemberCRUD(db=db)
    member = await crud.get_by_id(id=accept.id)
    await Permissions(user=user).permission_validator_for_company_member(member=member)
    return await crud.accept_invite(id=accept.id, member=member)


@router.post("/decline_invite", response_model=schemas_cm.ResponseMessage)
async def decline_invite(decline: schemas_cm.AcceptDecline, user = Depends(read_users_me)) -> schemas_cm.ResponseMessage:
    crud = CompanyMemberCRUD(db=db)
    member = await crud.get_by_id(id=decline.id)
    await Permissions(user=user).permission_validator_for_company_member(member=member)
    return await crud.decline_invite(id=decline.id, member=member)


@router.post("/ignore_invite", response_model=schemas_cm.ResponseMessage)
async def ignore_invite(decline: schemas_cm.AcceptDecline, user = Depends(read_users_me)) -> schemas_cm.ResponseMessage:
    """ To stop spaming invites from company user can ignore it """

    crud = CompanyMemberCRUD(db=db)
    member = await crud.get_by_id(id=decline.id)
    await Permissions(user=user).permission_validator_for_company_member(member=member)
    return await crud.ignore_invite(id=decline.id, member=member)


@router.post("/request_member_status", response_model=schemas_cm.ResponseMessage)
async def request_member_status(company_id: int, user = Depends(read_users_me)) -> schemas_cm.ResponseMessage:
    await Permissions(user=user).validate_token()
    crud = CompanyMemberCRUD(db=db)
    return await crud.request_member_status(company_id=company_id, user_id=user.id)


@router.post("/accept_member_status", response_model=schemas_cm.ResponseMessage)
async def accept_member_status(accept: schemas_cm.AcceptDecline, user = Depends(read_users_me)) -> schemas_cm.ResponseMessage:
    crud = CompanyMemberCRUD(db=db)
    member = await crud.get_by_id(id=accept.id)
    company = await CompanyCRUD(db=db).get_by_id(id=member.company_id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    
    return await crud.accept_member_status(member=member)


@router.post("/decline_member_status", response_model=schemas_cm.ResponseMessage)
async def decline_member_status(decline: schemas_cm.AcceptDecline, user = Depends(read_users_me)) -> schemas_cm.ResponseMessage:
    crud = CompanyMemberCRUD(db=db)
    member = await crud.get_by_id(id=decline.id)
    company = await CompanyCRUD(db=db).get_by_id(id=member.company_id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)    
    return await crud.decline_member_status(member=member)


@router.get("/{id}/users", response_model=schemas_cm.UsersListInCompany)
async def get_users_list(id: int = id, user = Depends(read_users_me)) -> schemas_cm.UsersListInCompany:
    """ Returning all active members of company ()"""
    await Permissions(user=user).validate_token()
    crud = CompanyMemberCRUD(db=db)
    return await crud.users_in_company(user_id=user.id, company_id=id)

@router.post("/provide_admin", response_model=schemas_cm.ResponseMessage)
async def provide_admin(data: schemas_cm.ProvideAdminStatus, user = Depends(read_users_me)) -> schemas_cm.ResponseMessage:
    company = await CompanyCRUD(db=db).get_by_id(id=data.company_id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    crud = CompanyMemberCRUD(db=db)
    return await crud.provide_admin_status(company_id=data.company_id, user_id=data.user_id)


@router.post("/remove_admin", response_model=schemas_cm.ResponseMessage)
async def remove_admin(data: schemas_cm.ProvideAdminStatus, user = Depends(read_users_me)) -> schemas_cm.ResponseMessage:
    company = await CompanyCRUD(db=db).get_by_id(id=data.company_id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    crud = CompanyMemberCRUD(db=db)
    return await crud.remove_admin_status(company_id=data.company_id, user_id=data.user_id)




