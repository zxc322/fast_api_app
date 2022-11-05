from typing import Union, Dict

from utils.exceptions import MyExceptions
from schemas.user import UserRsposneId
from schemas.company import ReturnCompany
from schemas.companies_members import CompanyMemberModel
from repositories.company import CompanyCRUD
from repositories.companies_members import CompanyMemberCRUD
from db.connection import database as db

class Permissions:

    def __init__(self, user: Union[UserRsposneId, Dict]) -> None:
        self.user = user
        self.exception = MyExceptions

    async def validate_token(self):
        if isinstance(self.user, dict):
            raise await self.exception().credentials_exception()

    async def permission_validator_for_user(self, id: int):
        await self.validate_token()        
        if self.user.id != id:
            raise await self.exception().permission_denied()

    async def permission_validator_for_company_owner(self, company: ReturnCompany):
        await self.validate_token()
        if self.user.id != company.owner_id:
            admin = await CompanyMemberCRUD(db=db).is_company_admin(
                user_id=self.user.id, company_id=company.id)
            if not admin:
                raise await self.exception().permission_denied()

    async def permission_validator_for_company_member(self, member: CompanyMemberModel):
        await self.validate_token()
        if self.user.id != member.member_id:
            raise await self.exception().permission_denied()

    async def read_users_results(self, user_id: int, company: ReturnCompany):
        await self.permission_validator_for_company_owner(company)
        member = await CompanyMemberCRUD(db=db).check_is_user_active_company_member(
                user_id=user_id, company_id=company.id)
        print('backend member', member)
        if not member:
            raise await self.exception().permission_denied()
    