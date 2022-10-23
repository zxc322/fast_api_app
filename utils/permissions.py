from typing import Union, Dict

from utils.exceptions import credentials_exception, permission_denied
from schemas.user import UserRsposneId
from schemas.company import Company



class Permissions:

    def __init__(self, user: Union[UserRsposneId, Dict]) -> None:
        self.user = user

    async def validate_token(self):
        print('type', type(self.user))
        if isinstance(self.user, dict):
            print('validate error')
            raise credentials_exception

    async def permission_validator_for_user(self, id: int):
        await self.validate_token()        
        if self.user.id != id:
            raise permission_denied

    async def permission_validator_for_company(self, id: int, company: Company):
        await self.validate_token()
        if self.user.id != company.owner_id:
            raise permission_denied

    