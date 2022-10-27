from typing import Union, Dict

from utils.exceptions import MyExceptions # credentials_exception, permission_denied
from schemas.user import UserRsposneId
from schemas.company import ReturnCompany
from schemas.companies_members import CompanyMemberModel
from repositories.company import CompanyCRUD
from repositories.companies_members import CompanyMemberCRUD
from db.models import companies as DBCompany, company_members as DBCompanies_members

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
            admin = await CompanyMemberCRUD(db_company_members=DBCompanies_members).is_company_admin(
                user_id=self.user.id, company_id=company.id)
            print('admin', admin)
            if not admin:
                raise await self.exception().permission_denied()

    async def permission_validator_for_company_member(self, member: CompanyMemberModel):
        await self.validate_token()
        if self.user.id != member.member_id:
            raise await self.exception().permission_denied()

    