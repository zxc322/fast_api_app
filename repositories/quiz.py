from typing import Optional
import math
from sqlalchemy import select, func

from datetime import datetime
from schemas import quiz as schema_q
from repositories.services.pagination import paginate_data
from repositories.services.generic_database import GenericDatabase


class QuizCRUD(GenericDatabase):

    async def get_by_name(self, name: str, company_id: int) -> Optional[schema_q.CheckQuiz]:
        quiz = await self.db.fetch_one(self.quiz_table.select().where(
            self.quiz_table.c.name == name,
            self.quiz_table.c.company_id == company_id,
            self.quiz_table.c.deleted_at == None))
        return schema_q.CheckQuiz(**quiz) if quiz else None



    async def create_quiz(self, quiz: schema_q.CreateQuiz) -> schema_q.QuizResponseMessage:
        if await self.get_by_name(name=quiz.name, company_id=quiz.company_id):
            raise await self.exception().quiz_already_exists(name=quiz.name)
            
        now = datetime.utcnow()
        quiz_data = dict(name=quiz.name, description=quiz.description, frequency=quiz.frequency,
            created_at=now, updated_at=now, company_id=quiz.company_id)
        quiz_id = await super().insert_values(table=self.quiz_table, values=quiz_data)

        for question in quiz.questions:
            upd_data=dict(question)
            upd_data['quiz_id'] = quiz_id   
            await super().insert_values(table=self.question_table, values=upd_data)          

        return schema_q.QuizResponseMessage(message=f'New quiz <{quiz.name}> have been created.')
        

    async def get_question_by_id(self, id: int) -> schema_q.ReturnQuestion:
        
        company_query = select(self.quiz_table).subquery()
        query = select(self.question_table, company_query).select_from(
            self.question_table.join(company_query)).where(self.question_table.c.id == id)        

        question = await self.db.fetch_one(query=query)
        if not question:
            raise await self.exception().question_was_not_found(id=id)
        return schema_q.ReturnQuestion(**question)


    async def append_option(self, options_in: schema_q.AppendOption) -> schema_q.ResponseId:
        question = await self.db.fetch_one(select(self.question_table.c.options).where(
            self.question_table.c.id==options_in.question_id))
        
        # If option in question already rause exc
        for opt in options_in.options:
            if opt in question.options:
                raise await self.exception().option_already_exists(name=opt)

        await self.db.execute(self.question_table.update().values(
            options=question.options + options_in.options).where(
            self.question_table.c.id==options_in.question_id))
        return schema_q.ResponseId(id=options_in.question_id)


    async def delete_option(self, option: schema_q.DeleteOptionByName) -> schema_q.ResponseId:
        question = await self.db.fetch_one(select(self.question_table.c.options).where(self.question_table.c.id==option.question_id))
        
        # If option with index not in options range or length options list <=2 raise exc 
        if option.name not in question.options:
            raise await self.exception().option_was_not_found(name=option.name)
        if len(question.options) <= 2:
            raise await self.exception().low_options_quantity(id=option.question_id)

        question.options.remove(option.name)

        await self.db.execute(self.question_table.update().values(
            options=question.options).where(
            self.question_table.c.id==option.question_id))
        return schema_q.ResponseId(id=option.question_id)


    async def get_quiz_by_id(self, id: int) -> schema_q.FullQuizInfo:
        quiz = await self.db.fetch_one(self.quiz_table.select().where(self.quiz_table.c.id==id, self.quiz_table.c.deleted_at==None))
        if not quiz:
            raise await self.exception().quiz_not_found(id=id)
        return schema_q.FullQuizInfo(**dict(quiz))

    async def append_question(self, question: schema_q.AppendQuestion) -> schema_q.ResponseId:
        # chek if this question alrdy exists in this quiz 
        if await self.db.fetch_one(self.question_table.select().where(
            self.question_table.c.question==question.question, self.question_table.c.quiz_id==question.quiz_id)):
            raise await self.exception().question_already_exists(name=question.question)
            
        return schema_q.ResponseId(id=await self.db.execute(self.question_table.insert().values(dict(question))))

    
    async def update_question(self, question: schema_q.UpdateQuestion) -> schema_q.ResponseId:
        updated_data = question.dict(skip_defaults=True)
        await self.db.execute(self.question_table.update().values(updated_data).where(self.question_table.c.id==question.id))
        return schema_q.ResponseId(id=question.id)


    async def delete_question(self, question) -> schema_q.ResponseId:
        questions = await self.db.fetch_all(self.question_table.select().where(self.question_table.c.quiz_id==question.quiz_id))
        if not questions or len(questions) <= 2:
            raise await self.exception().low_questions_quantity(id=question.quiz_id)
        await self.db.execute(self.question_table.delete().where(self.question_table.c.id==question.id))
        return schema_q.ResponseId(id=question.id)


    async def get_quiz_list(self, company_id: int, page: int = 1, limit: int = 10) -> schema_q.CompaniesQuiezes:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        query = self.quiz_table.select().where(
            self.quiz_table.c.company_id==company_id,
            self.quiz_table.c.deleted_at==None
            ).limit(limit).offset(skip)

        quizes = await self.db.fetch_all(query=query)
        count = await self.db.fetch_one(select(func.count().label('quizes')).select_from(self.quiz_table).where(
            self.quiz_table.c.company_id==company_id,
            self.quiz_table.c.deleted_at==None
        ))
    
        total_pages = math.ceil(count.quizes/limit)
        pagination = await paginate_data(page, count.quizes, total_pages, end, limit, url='quiz/company')
        return schema_q.CompaniesQuiezes(quizes=quizes, pagination=pagination)


    async def update_quiz(self, quiz: schema_q.UpdateQuiz) -> schema_q.ResponseId:
        updated_data = quiz.dict(skip_defaults=True)
        updated_data.update(updated_at=datetime.utcnow())
        await self.db.execute(self.quiz_table.update().values(updated_data).where(self.quiz_table.c.id==quiz.id))
        return schema_q.ResponseId(id=quiz.id)

    async def remove_quiz(self, id: int) -> schema_q.ResponseId:
        await self.db.execute(self.quiz_table.update().values(deleted_at=datetime.utcnow()).where(self.quiz_table.c.id==id))
        return schema_q.ResponseId(id=id)


    async def get_quiz_ids_list_for_redis(self, company_id: int) -> list:
        """ Returns list with ids of chosen companys quizes ( 4 redis) """

        quizes = await self.db.fetch_all(select(self.quiz_table.c.id).where(
            self.quiz_table.c.company_id==company_id,
            self.quiz_table.c.deleted_at==None
            ))      
    
        return [dict(i).get('id') for i in quizes]
