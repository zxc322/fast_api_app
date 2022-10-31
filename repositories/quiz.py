from typing import Optional
import math
from sqlalchemy import select, func

from db.connection import database
from datetime import datetime
from db.models import quiz as DBQuiz, question as DBQuestion, option as DBOption, companies as DBCompany
from schemas.quiz import UpdateQuiz, CompaniesQuiezes, AppendQuestion, FullQuizInfo, UpdateOption, AppendOption, CreateQuiz, CheckQuiz, QuizResponseMessage, ReturnQuestion, ResponseId, FullOptionData, UpdateQuestion

from repositories.services.pagination import paginate_data
from utils.exceptions import CustomError, MyExceptions


class QuizCRUD:
    def __init__(self) -> None:
        self.db_quiz = DBQuiz
        self.db_question = DBQuestion
        self.db_option = DBOption
        self.exc = MyExceptions


    async def get_by_name(self, name: str, company_id: int) -> Optional[CheckQuiz]:
        quiz = await database.fetch_one(self.db_quiz.select().where(
            self.db_quiz.c.name == name,
            self.db_quiz.c.company_id == company_id,
            self.db_quiz.c.deleted_at == None))
        return CheckQuiz(**quiz) if quiz else None



    async def create_quiz(self, quiz: CreateQuiz) -> QuizResponseMessage:
        if await self.get_by_name(name=quiz.name, company_id=quiz.company_id):
            raise await self.exc().quiz_already_exists(name=quiz.name)
            
        now = datetime.utcnow()
        quiz_data = dict(name=quiz.name, description=quiz.description, frequency=quiz.frequency,
            created_at=now, updated_at=now, company_id=quiz.company_id)
        new_quiz_id = await database.execute(self.db_quiz.insert().values(quiz_data))
        questions = quiz.questions

        for question in questions:
            question_data = dict(question=question.question, quiz_id=new_quiz_id)
            new_question_id = await database.execute(self.db_question.insert().values(question_data))
            for option in question.options:
                await database.execute(self.db_option.insert().values(
                    option=option.option, is_right=option.is_right, question_id=new_question_id))

        return QuizResponseMessage(message=f'New quiz <{quiz.name}> have been created.')
        

    async def get_question_by_id(self, id: int) -> ReturnQuestion:

        company_query = select(self.db_quiz).subquery()
        query = select(self.db_question, company_query).select_from(
            self.db_question.join(company_query)).where(self.db_question.c.id == id)        

        question = await database.fetch_one(query=query)
        if not question:
            raise await self.exc().question_was_not_found(id=id)
        return ReturnQuestion(**question)

    async def get_option_by_id(self, id: int) -> FullOptionData:
        option = await database.fetch_one(self.db_option.select().where(self.db_option.c.id==id))
        if not option:
            raise await self.exc().option_was_not_found(id=id)
        option = dict(option)
        return FullOptionData(**option)


    async def append_option(self, option: AppendOption) -> ResponseId: 
        return ResponseId(id=await database.execute(self.db_option.insert().values(dict(option))))

    
    async def update_option(self, option: UpdateOption) -> ResponseId:
        updated_data = option.dict(skip_defaults=True)
        id = updated_data.pop('id')
        await database.execute(self.db_option.update().values(updated_data).where(self.db_option.c.id==id))
        return ResponseId(id=id)


    async def delete_option(self, option: FullOptionData) -> ResponseId:
        options = await database.fetch_all(self.db_option.select().where(self.db_option.c.question_id==option.question_id))
        if not options or len(options) <= 2:
            raise await self.exc().low_options_quantity(id=option.question_id)
        await database.execute(self.db_option.delete().where(self.db_option.c.id==option.id))
        return ResponseId(id=option.id)


    async def get_quiz_by_id(self, id: int) -> FullQuizInfo:
        quiz = await database.fetch_one(self.db_quiz.select().where(self.db_quiz.c.id==id, self.db_quiz.c.deleted_at==None))
        if not quiz:
            raise await self.exc().quiz_not_found(id=id)
        r = dict(quiz)    
        return FullQuizInfo(**r)

    async def append_question(self, question: AppendQuestion) -> ResponseId:
        # chek if this question alrdy exists in this quiz 
        if await database.fetch_one(self.db_question.select().where(
            self.db_question.c.question==question.question, self.db_question.c.quiz_id==question.quiz_id)):
            raise await self.exc().question_already_exists(name=question.question) 
        new_question_id = await database.execute(self.db_question.insert().values(question=question.question, quiz_id=question.quiz_id))
        for opt in question.options:
            await database.execute(self.db_option.insert().values(option=opt.option, is_right=opt.is_right, question_id=new_question_id))
        return ResponseId(id=new_question_id)

    
    async def update_question(self, question: UpdateQuestion) -> ResponseId:
        await database.execute(self.db_question.update().values(question=question.question).where(self.db_question.c.id==question.id))
        return ResponseId(id=question.id)


    async def delete_question(self, question) -> ResponseId:
        questions = await database.fetch_all(self.db_question.select().where(self.db_question.c.quiz_id==question.quiz_id))
        if not questions or len(questions) <= 2:
            raise await self.exc().low_questions_quantity(id=question.quiz_id)
        await database.execute(self.db_question.update().values(deleted_at=datetime.utcnow()).where(self.db_question.c.id==question.id))
        return ResponseId(id=question.id)

    async def get_quiz_list(self, company_id: int, page: int = 1, limit: int = 10) -> CompaniesQuiezes:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        query = self.db_quiz.select().where(
            self.db_quiz.c.company_id==company_id,
            self.db_quiz.c.deleted_at==None
            ).limit(limit).offset(skip)

        quizes = await database.fetch_all(query=query)
        count = await database.fetch_one(select(func.count().label('quizes')).select_from(self.db_quiz).where(
            self.db_quiz.c.company_id==company_id,
            self.db_quiz.c.deleted_at==None
        ))
    
        total_pages = math.ceil(count.quizes/limit)
        pagination = await paginate_data(page, count.quizes, total_pages, end, limit, url='quiz/company')
        return CompaniesQuiezes(quizes=quizes, pagination=pagination)


    async def update_quiz(self, quiz: UpdateQuiz) -> ResponseId:
        updated_data = quiz.dict(skip_defaults=True)
        updated_data.update(updated_at=datetime.utcnow())
        await database.execute(self.db_quiz.update().values(updated_data).where(self.db_quiz.c.id==quiz.id))
        return ResponseId(id=quiz.id)

    async def remove_quiz(self, id: int) -> ResponseId:
        await database.execute(self.db_quiz.update().values(deleted_at=datetime.utcnow()).where(self.db_quiz.c.id==id))
        return ResponseId(id=id)