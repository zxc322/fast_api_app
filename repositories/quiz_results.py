import math
from sqlalchemy import select, func
from typing import Dict

from db.connection import database
from datetime import datetime
from schemas import quiz_results as schema_qr
from schemas import quiz as schema_q
from repositories.services import quiz_utils
from repositories.services.redis_utils import save_to_redis
from utils.exceptions import MyExceptions


# from db.models import quiz, question, option

def generate_quiz_query(quiz_id):
    return f'SELECT quiz.id as quiz_id,\
                quiz.name as quiz_name,\
                frequency,\
                question.id as question_id,\
                question.question as question,\
                option.id as option_id,\
                option.option as option,\
                option.is_right as is_right,\
                option.question_id as option_question_id\
                FROM quiz\
                INNER JOIN question \
                ON quiz.id = question.quiz_id\
                JOIN option \
                ON question.id = option.question_id\
                WHERE quiz.id = {quiz_id} AND quiz.deleted_at IS NULL\
                AND question.deleted_at IS NULL'




class QuizResultCRUD:
    def __init__(self, db_quiz, db_question, db_option, db_quiz_result, db_avarage_mark) -> None:
        self.db_quiz = db_quiz
        self.db_question = db_question
        self.db_option = db_option
        self.db_quiz_result = db_quiz_result
        self.db_avarage_mark = db_avarage_mark
        self.exc = MyExceptions


    async def get_ui_quiz(self, quiz_id: int) -> schema_q.QuizForUser:
        queryset = await database.fetch_all(generate_quiz_query(quiz_id=quiz_id))
        question_count = await database.fetch_one(select(func.count().label('total')).select_from(
            self.db_question).where(self.db_question.c.quiz_id==quiz_id,
            self.db_question.c.deleted_at==None))

        if not queryset:
            raise await self.exc().quiz_not_found(id=quiz_id)
        result = await quiz_utils.generate_nested_quiz(queryset=queryset, question_count=question_count)
        return schema_q.QuizForUser(**result)


    async def parse_quiz_result(self, income_quiz: schema_qr.IncomeQuiz, user_id: int) -> schema_qr.ResultsFeedback:
        await save_to_redis(user_id=user_id, income_quiz=income_quiz)
        result = await quiz_utils.generate_users_results_as_dict(user_id=user_id, income_quiz=income_quiz)
        await database.execute(self.db_quiz_result.insert().values(result))
        await quiz_utils.rewrite_avg_mark(average_table=self.db_avarage_mark, data=result)        
        return schema_qr.ResultsFeedback(**result)


    
        
        
        
 

        
