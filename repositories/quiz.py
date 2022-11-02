from typing import Optional
import math
from sqlalchemy import select, func
from databases import Database


from datetime import datetime
from db.models import quiz as DBQuiz, question as DBQuestion
from schemas import quiz as schema_q

from repositories.services.pagination import paginate_data
from utils.exceptions import MyExceptions


class QuizCRUD:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.db_quiz = DBQuiz
        self.db_question = DBQuestion
        self.exc = MyExceptions


    async def get_by_name(self, name: str, company_id: int) -> Optional[schema_q.CheckQuiz]:
        quiz = await self.db.fetch_one(self.db_quiz.select().where(
            self.db_quiz.c.name == name,
            self.db_quiz.c.company_id == company_id,
            self.db_quiz.c.deleted_at == None))
        return schema_q.CheckQuiz(**quiz) if quiz else None



    async def create_quiz(self, quiz: schema_q.CreateQuiz) -> schema_q.QuizResponseMessage:
        if await self.get_by_name(name=quiz.name, company_id=quiz.company_id):
            raise await self.exc().quiz_already_exists(name=quiz.name)
            
        now = datetime.utcnow()
        quiz_data = dict(name=quiz.name, description=quiz.description, frequency=quiz.frequency,
            created_at=now, updated_at=now, company_id=quiz.company_id)
        quiz_id = await self.db.execute(self.db_quiz.insert().values(quiz_data))

        for question in quiz.questions:
            upd_data=dict(question)
            await self.db.execute(self.db_question.insert().values(quiz_id=quiz_id, **upd_data))           

        return schema_q.QuizResponseMessage(message=f'New quiz <{quiz.name}> have been created.')
        

    async def get_question_by_id(self, id: int) -> schema_q.ReturnQuestion:
        
        company_query = select(self.db_quiz).subquery()
        query = select(self.db_question, company_query).select_from(
            self.db_question.join(company_query)).where(self.db_question.c.id == id)        

        question = await self.db.fetch_one(query=query)
        if not question:
            raise await self.exc().question_was_not_found(id=id)
        return schema_q.ReturnQuestion(**question)


    async def get_option_by_id(self, id: int) :
        pass


    async def append_option(self, options_in: schema_q.AppendOption) -> schema_q.ResponseId:
        question = await self.db.fetch_one(select(self.db_question.c.options).where(self.db_question.c.id==options_in.question_id))
        
        # If option in question already rause exc
        for opt in options_in.options:
            if opt in question.options:
                raise await self.exc().option_already_exists(name=opt)

        await self.db.execute(self.db_question.update().values(
            options=question.options + options_in.options).where(
            self.db_question.c.id==options_in.question_id))
        return schema_q.ResponseId(id=options_in.question_id)




    async def delete_option(self, option_idx: schema_q.DeleteOptionByIndex) -> schema_q.ResponseId:
        question = await self.db.fetch_one(select(self.db_question.c.options).where(self.db_question.c.id==option_idx.question_id))
        
        # If option with index not in options range or length options list <=2 raise exc 
        try:
            question.options[option_idx.option_idx]
        except IndexError:
                raise await self.exc().option_was_not_found(idx=option_idx.option_idx)
        if len(question.options) <= 2:
            raise await self.exc().low_options_quantity(id=option_idx.question_id)

        question.options.pop(option_idx.option_idx)

        await self.db.execute(self.db_question.update().values(
            options=question.options).where(
            self.db_question.c.id==option_idx.question_id))
        return schema_q.ResponseId(id=option_idx.question_id)


    async def get_quiz_by_id(self, id: int) -> schema_q.FullQuizInfo:
        quiz = await self.db.fetch_one(self.db_quiz.select().where(self.db_quiz.c.id==id, self.db_quiz.c.deleted_at==None))
        if not quiz:
            raise await self.exc().quiz_not_found(id=id)
        return schema_q.FullQuizInfo(**dict(quiz))

    async def append_question(self, question: schema_q.AppendQuestion) -> schema_q.ResponseId:
        # chek if this question alrdy exists in this quiz 
        if await self.db.fetch_one(self.db_question.select().where(
            self.db_question.c.question==question.question, self.db_question.c.quiz_id==question.quiz_id)):
            raise await self.exc().question_already_exists(name=question.question)
            
        return schema_q.ResponseId(id=await self.db.execute(self.db_question.insert().values(dict(question))))

    
    async def update_question(self, question: schema_q.UpdateQuestion) -> schema_q.ResponseId:
        updated_data = question.dict(skip_defaults=True)
        await self.db.execute(self.db_question.update().values(updated_data).where(self.db_question.c.id==question.id))
        return schema_q.ResponseId(id=question.id)


    async def delete_question(self, question) -> schema_q.ResponseId:
        questions = await self.db.fetch_all(self.db_question.select().where(self.db_question.c.quiz_id==question.quiz_id))
        if not questions or len(questions) <= 2:
            raise await self.exc().low_questions_quantity(id=question.quiz_id)
        await self.db.execute(self.db_question.delete().where(self.db_question.c.id==question.id))
        return schema_q.ResponseId(id=question.id)

    async def get_quiz_list(self, company_id: int, page: int = 1, limit: int = 10) -> schema_q.CompaniesQuiezes:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        query = self.db_quiz.select().where(
            self.db_quiz.c.company_id==company_id,
            self.db_quiz.c.deleted_at==None
            ).limit(limit).offset(skip)

        quizes = await self.db.fetch_all(query=query)
        count = await self.db.fetch_one(select(func.count().label('quizes')).select_from(self.db_quiz).where(
            self.db_quiz.c.company_id==company_id,
            self.db_quiz.c.deleted_at==None
        ))
    
        total_pages = math.ceil(count.quizes/limit)
        pagination = await paginate_data(page, count.quizes, total_pages, end, limit, url='quiz/company')
        return schema_q.CompaniesQuiezes(quizes=quizes, pagination=pagination)


    async def update_quiz(self, quiz: schema_q.UpdateQuiz) -> schema_q.ResponseId:
        updated_data = quiz.dict(skip_defaults=True)
        updated_data.update(updated_at=datetime.utcnow())
        await self.db.execute(self.db_quiz.update().values(updated_data).where(self.db_quiz.c.id==quiz.id))
        return schema_q.ResponseId(id=quiz.id)

    async def remove_quiz(self, id: int) -> schema_q.ResponseId:
        await self.db.execute(self.db_quiz.update().values(deleted_at=datetime.utcnow()).where(self.db_quiz.c.id==id))
        return schema_q.ResponseId(id=id)