from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import date
from typing import List, Dict
from schemas.company import PublicCompany
from schemas.user import PublicUser


class Invite(BaseModel):
    company_id: int
    user_id: int


class ResponseMessage(BaseModel):
    message: str


class PublicInvite(BaseModel):
    id: int
    invited: date
    company: PublicCompany


class MyInvites(BaseModel):
    invites: List[PublicInvite] = []
    pagination: Dict

    class Config:
        orm_mode = True

class UserInCompany(BaseModel):
    id: int
    active_member_from: date
    user: PublicUser

class UsersListInCompany(BaseModel):
    users: List[UserInCompany]
    pagination: Dict


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

class AcceptDecline(BaseModel):
    id: int

