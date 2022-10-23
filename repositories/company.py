from typing import Optional, Union
from sqlalchemy.orm import Session
from typing import Dict
import math
from db.connection import database
from datetime import datetime

from db.models import user as DBUser, company as DBCompany
from schemas.company import CreateCompany, PublicCompany, ResponseCompanyId, UpdateCompany, Company, Companies
from security.auth import get_password_hash
from repositories.service import Log, paginate_data
from utils.exceptions import CustomError


class CompanyCRUD:

    def __init__(self, db_company: DBCompany = None):
        self.db_company = db_company
    
    async def get_by_name(self, name: str) -> Optional[PublicCompany]:
        company = await database.fetch_one(self.db_company.select().where(
            self.db_company.c.name == name,
            self.db_company.c.deleted_at == None))
        return PublicCompany(**company) if company else None

    async def get_by_id(self, id: int) -> Company:
        company = await database.fetch_one(self.db_company.select().where(
            self.db_company.c.id == id,
            self.db_company.c.deleted_at == None))
        if not company:
            raise CustomError(company_id=id)
        return Company(**company)

    async def create(self, company_in: CreateCompany, owner: int) -> ResponseCompanyId:
        now = datetime.utcnow()
        company = self.db_company.insert().values(
            name=company_in.name,
            description=company_in.description,
            visible=company_in.visible,
            created_at=now,
            updated_at=now,
            owner_id=owner
        )      
        
        return ResponseCompanyId(id=await database.execute(company))


    async def update(self, id: int, company_in: UpdateCompany) -> ResponseCompanyId:
        now = datetime.utcnow()     
        updated_data = company_in.dict(skip_defaults=True)
        updated_data['updated_at'] = now
        u = self.db_company.update().values(updated_data).where(self.db_company.c.id==id)
        await database.execute(u)
        return ResponseCompanyId(id=id)

    async def remove(self, id: int) -> ResponseCompanyId:
        company = await self.get_by_id(id=id)
        u = self.db_company.update().values(deleted_at=datetime.utcnow(), name='[REMOVED] ' + company.name).where(self.db_company.c.id==id)
        await database.execute(u)
        return ResponseCompanyId(id=id)


    async def get_companies(self, page: int = 1, limit: int = 10) -> Companies:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        users_on_page = self.db_company.select().where(self.db_company.c.deleted_at == None).offset(skip).limit(limit)
        total_users =  self.db_company.select().where(self.db_company.c.deleted_at == None)
        count = len(await database.fetch_all(total_users))
        
        queryset = await database.fetch_all(users_on_page)
        total_pages = math.ceil(count/limit)

        users = [dict(result) for result in queryset]
        pagination = await paginate_data(page, count, total_pages, end, limit)
        return Companies(users=users, pagination=pagination)

        
