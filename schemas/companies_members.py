from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import date
from typing import List, Dict
from schemas import generic


class Invite(BaseModel):
    company_id: int
    user_id: int


class ResponseMessage(BaseModel):
    message: str


class PublicInvite(BaseModel):
    member_id: int
    invited: date
    company_id: int
    company_name: str
    company_description: str
    owner_id: int


class MyInvites(BaseModel):
    invites: List[PublicInvite] = []
    pagination: Dict

    class Config:
        orm_mode = True

class UserInCompany(BaseModel):
    member_id: int
    company_id: int
    active_member_from: date
    is_company_admin: Optional[bool] = False
    user_id: int
    username: str

class UsersListInCompany(BaseModel):
    users: List[UserInCompany]



class CompanyMemberModel(BaseModel):
    id: int
    active_member: Optional[date]
    invited: Optional[date]
    requested: Optional[date]
    ignored_by_user: Optional[bool]
    ignored_by_owner: Optional[bool]
    created_at: date
    updated_at: date
    company_id: int
    member_id: int


class AcceptDecline(generic.ResponseId):
    pass

class ProvideAdminStatus(Invite):
    pass