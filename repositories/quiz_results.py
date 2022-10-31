from sqlalchemy import func
from sqlalchemy.sql import select


from db.connection import database
from schemas import quiz_results as schema_qr
from schemas import quiz as schema_q
from repositories.services import quiz_utils
from repositories.services.redis_utils import save_to_redis
from utils.exceptions import MyExceptions
from db.models import quiz as DBQuiz, question as DBQuestion, option as DBOption, avarage_mark as DBAvg_mark, quiz_result as DBQuiz_result


class QuizResultCRUD:
    def __init__(self) -> None:
        self.db_quiz = DBQuiz
        self.db_question = DBQuestion
        self.db_option = DBOption
        self.db_quiz_result = DBQuiz_result
        self.db_avarage_mark = DBAvg_mark
        self.exc = MyExceptions


    async def get_ui_quiz(self, quiz_id: int) -> schema_q.QuizForUser:

        
        query_joins = self.db_question.join(self.db_quiz).join(self.db_option)

        query = select(
            self.db_quiz.c.id.label('quiz_id'),
            self.db_quiz.c.name.label('quiz_name'),
            self.db_quiz.c.frequency.label('frequency'),
            self.db_question.c.id.label('question_id'),
            self.db_question.c.question.label('question'),
            self.db_option.c.id.label('option_id'),
            self.db_option.c.option.label('option'),
            self.db_option.c.is_right.label('is_right'),
            self.db_option.c.question_id.label('option_question_id')
        ).select_from(query_joins).where(self.db_quiz.c.id==quiz_id, self.db_quiz.c.deleted_at==None)

        queryset = await database.fetch_all(query=query)

        question_count = await database.fetch_one(select(func.count().label('total')).select_from(
            self.db_question).where(self.db_question.c.quiz_id==quiz_id,
            self.db_question.c.deleted_at==None))

        if not queryset:
            raise await self.exc().quiz_not_found(id=quiz_id)
        result = await quiz_utils.generate_nested_quiz(queryset=queryset, question_count=question_count)
        return schema_q.QuizForUser(**result)


    async def parse_quiz_result(self, income_quiz: schema_qr.IncomeQuiz, user_id: int) -> schema_qr.ResultsFeedback:
        if income_quiz.quiz_id == 0:
            raise await self.exc().id_is_0() 
        await save_to_redis(user_id=user_id, income_quiz=income_quiz)
        result = await quiz_utils.generate_users_results_as_dict(user_id=user_id, income_quiz=income_quiz)
        await database.execute(self.db_quiz_result.insert().values(result))
        await quiz_utils.rewrite_avg_mark(average_table=self.db_avarage_mark, data=result)        
        return schema_qr.ResultsFeedback(**result)


    
        
        
        
 

        
