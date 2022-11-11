from databases import Database
from sqlalchemy import select, func
from typing import Dict

from db import models 
from schemas import companies_members as schema_cm
from utils.exceptions import MyExceptions



class GenericDatabase:

    def __init__(self, db: Database):
        self.db = db
        self.company_members_table = models.company_members
        self.company_table = models.companies
        self.users_table = models.users
        self.quiz_table = models.quiz
        self.question_table = models.question
        self.avarage_mark_table=models.avarage_mark
        self.uiz_result_table = models.companies
        self.quiz_result_table=models.quiz_result
        self.exception = MyExceptions


    async def insert_values(self, table, values: Dict):
        return await self.db.execute(table.insert().values(values))

        
    
    async def company_members_join_company(self):
        query_joins = self.company_members_table.join(self.company_table)
        query = select(
            self.company_table.c.id.label('company_id'),
            self.company_table.c.name.label('company_name'),
            self.company_members_table.c.is_company_admin,
            self.company_members_table.c.active_member.label('active_from'),
            ).select_from(query_joins)
        
        return query