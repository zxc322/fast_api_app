from typing import Optional
import math
from datetime import datetime

from schemas import company as schema_c 
from repositories.services.pagination import paginate_data
from utils.exceptions import CustomError
from sqlalchemy import select, func
from repositories.services.generic_database import GenericDatabase


class CompanyCRUD(GenericDatabase):


    async def create(self, company_in: schema_c.CreateCompany, owner: int) -> schema_c.ResponseCompanyId:
        now = datetime.utcnow()
        values = dict(
            name=company_in.name,
            description=company_in.description,
            visible=company_in.visible,
            created_at=now,
            updated_at=now,
            owner_id=owner
        )
        company = await super().insert_values(table=self.company_table, values=values)

        # Adding owner as active member and admin of company

        values = dict(
                active_member=now,
                is_company_admin=True,
                member_id=owner,
                company_id=company,
                created_at=now,
                updated_at=now
            )
        await super().insert_values(table=self.company_members_table, values=values)

        return schema_c.ResponseCompanyId(id=company)

    
    async def get_by_name(self, name: str) -> Optional[schema_c.ReturnCompany]:
        company = await self.db.fetch_one(self.company_table.select().where(
            self.company_table.c.name == name,
            self.company_table.c.deleted_at == None))
        return schema_c.ReturnCompany(**company) if company else None

    
    async def get_by_id(self, id: int) -> schema_c.ReturnCompany:
        company = await self.db.fetch_one(self.company_table.select().where(
            self.company_table.c.id == id,
            self.company_table.c.deleted_at == None))
        if not company:
            if not id:
                id = '0'
            raise CustomError(company_id=id)
        return schema_c.ReturnCompany(**company)

    
    async def update(self, id: int, company_in: schema_c.UpdateCompany) -> schema_c.ResponseCompanyId:
        now = datetime.utcnow()     
        updated_data = company_in.dict(skip_defaults=True)
        updated_data['updated_at'] = now
        await self.db.execute(self.company_table.update().values(updated_data).where(
            self.company_table.c.id==id))
        return schema_c.ResponseCompanyId(id=id)

    
    async def remove(self, id: int) -> schema_c.ResponseCompanyId:
        company = await self.get_by_id(id=id)
        now = datetime.utcnow()
        deleted_data = {'deleted_at': now, 'name': '[REMOVED] ' + company.name, 'updated_at': now}
        await self.db.execute(self.company_table.update().values(deleted_data).where(
            self.company_table.c.id==id))
        return schema_c.ResponseCompanyId(id=id)


    async def get_companies(self, page: int = 1, limit: int = 10) -> schema_c.Companies:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        users_query = select(
            self.users_table.c.id.label('owner_id'), 
            self.users_table.c.username.label('owner_usename')).subquery()

        query = select(self.company_table.c.id.label('company_id'), 
            self.company_table.c.name.label('company_name'),
            self.company_table.c.description,
            self.company_table.c.created_at,
            users_query).select_from(self.company_table.join(users_query)).where(
                self.company_table.c.deleted_at==None,
                self.company_table.c.visible==True 
            ).limit(limit).offset(skip)
             
        count_query = select([func.count().label('total_companies')]).select_from(
            self.company_table).where(
                self.company_table.c.deleted_at==None,
                self.company_table.c.visible==True
            )

        companies = await self.db.fetch_all(query=query)
        count = await self.db.fetch_one(count_query)
        count = count.total_companies
        total_pages = math.ceil(count/limit)
        pagination = await paginate_data(page, count, total_pages, end, limit, url='company')
        return schema_c.Companies(companies=companies, pagination=pagination)

