from sqlalchemy import func
from sqlalchemy.sql import select
from databases import Database

from schemas import quiz_results as schema_qr
from schemas import quiz as schema_q
from repositories.services import quiz_utils
from repositories.services.redis_utils import save_to_redis
from utils.exceptions import MyExceptions
from db.models import quiz as DBQuiz, question as DBQuestion, avarage_mark as DBAvg_mark, quiz_result as DBQuiz_result


class QuizResultCRUD:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.db_quiz = DBQuiz
        self.db_question = DBQuestion
        self.db_quiz_result = DBQuiz_result
        self.db_avarage_mark = DBAvg_mark
        self.exc = MyExceptions


    async def get_ui_quiz(self, quiz_id: int) -> schema_q.QuizForUser:

        
        query_joins = self.db_question.join(self.db_quiz)

        query = select(
            self.db_quiz.c.id.label('quiz_id'),
            self.db_quiz.c.name.label('quiz_name'),
            self.db_quiz.c.frequency.label('frequency'),
            self.db_question.c.id.label('question_id'),
            self.db_question.c.question.label('question'),
            self.db_question.c.options.label('options'),
            self.db_question.c.right_answer.label('right_answer')
        ).select_from(query_joins).where(self.db_quiz.c.id==quiz_id, self.db_quiz.c.deleted_at==None).order_by(self.db_question.c.id)

        queryset = await self.db.fetch_all(query=query)

        question_count = await self.db.fetch_one(select(func.count().label('total')).select_from(
            self.db_question).where(self.db_question.c.quiz_id==quiz_id))

        if not queryset:
            raise await self.exc().quiz_not_found(id=quiz_id)
        data_in = schema_qr.QuizResponse(total_questions=question_count.total)
        return await quiz_utils.generate_nested_quiz(queryset=queryset, data_in=data_in)


    async def parse_quiz_result(self, income_quiz: schema_qr.IncomeQuiz, user_id: int) -> schema_qr.ResultsFeedback:
        if income_quiz.quiz_id == 0:
            raise await self.exc().id_is_0() 
        await save_to_redis(user_id=user_id, income_quiz=income_quiz)
        result = await quiz_utils.generate_users_results_as_dict(user_id=user_id, income_quiz=income_quiz)
        await self.db.execute(self.db_quiz_result.insert().values(result))
        await quiz_utils.rewrite_avg_mark(average_table=self.db_avarage_mark, data=result)        
        return schema_qr.ResultsFeedback(**result)


    
        
        
        
 

        
