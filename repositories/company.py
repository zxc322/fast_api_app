from typing import Optional
import math
from databases import Database
from datetime import datetime

from db.models import companies as DBCompany, users as DBUser
from schemas.company import CreateCompany, ResponseCompanyId, UpdateCompany, Companies, ReturnCompany
from repositories.services.pagination import paginate_data
from utils.exceptions import CustomError
from sqlalchemy import select, func


class CompanyCRUD:

    def __init__(self, db: Database):
        self.db = db
        self.db_company = DBCompany
    
    async def get_by_name(self, name: str) -> Optional[ReturnCompany]:
        company = await self.db.fetch_one(self.db_company.select().where(
            self.db_company.c.name == name,
            self.db_company.c.deleted_at == None))
        return ReturnCompany(**company) if company else None

    async def get_by_id(self, id: int) -> ReturnCompany:
        company = await self.db.fetch_one(self.db_company.select().where(
            self.db_company.c.id == id,
            self.db_company.c.deleted_at == None))
        if not company:
            if not id:
                id = '0'
            raise CustomError(company_id=id)
        return ReturnCompany(**company)

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
        
        return ResponseCompanyId(id=await self.db.execute(company))


    async def update(self, id: int, company_in: UpdateCompany) -> ResponseCompanyId:
        now = datetime.utcnow()     
        updated_data = company_in.dict(skip_defaults=True)
        updated_data['updated_at'] = now
        u = self.db_company.update().values(updated_data).where(self.db_company.c.id==id)
        await self.db.execute(u)
        return ResponseCompanyId(id=id)

    async def remove(self, id: int) -> ResponseCompanyId:
        company = await self.get_by_id(id=id)
        now = datetime.utcnow()
        deleted_data = {'deleted_at': now, 'name': '[REMOVED] ' + company.name, 'updated_at': now}
        u = self.db_company.update().values(deleted_data).where(self.db_company.c.id==id)
        await self.db.execute(u)
        return ResponseCompanyId(id=id)


    async def get_companies(self, page: int = 1, limit: int = 10) -> Companies:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        users_query = select(DBUser.c.id.label('owner_id'), DBUser.c.username.label('owner_usename')).subquery()

        query = select(self.db_company.c.id.label('company_id'), 
            self.db_company.c.name.label('company_name'),
            self.db_company.c.description,
            self.db_company.c.created_at,
            users_query).select_from(self.db_company.join(users_query)).where(
                self.db_company.c.deleted_at==None,
                self.db_company.c.visible==True 
            ).limit(limit).offset(skip)
             
        count_query = select([func.count().label('total_companies')]).select_from(self.db_company).where(
            self.db_company.c.deleted_at==None,
            self.db_company.c.visible==True
        )

        companies = await self.db.fetch_all(query=query)
        count = await self.db.fetch_one(count_query)
        count = count.total_companies
        total_pages = math.ceil(count/limit)
        pagination = await paginate_data(page, count, total_pages, end, limit, url='company')
        return Companies(companies=companies, pagination=pagination)


        
