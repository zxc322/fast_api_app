from sqlalchemy import func
from sqlalchemy.sql import select

from schemas import quiz_results as schema_qr
from schemas import quiz as schema_q
from repositories.services import quiz_results as quiz_service
from repositories.services.write_quiz_results_to_database import InsertQuizResultToDatabase
from repositories.services import nested_quiz_for_client as UI_service
from repositories.services.generic_database import GenericDatabase


class QuizResultCRUD(GenericDatabase):
  

    async def get_ui_quiz(self, quiz_id: int) -> schema_q.QuizForUser:
     
        query_joins = self.question_table.join(self.quiz_table)
        query = select(
            self.quiz_table.c.id.label('quiz_id'),
            self.quiz_table.c.name.label('quiz_name'),
            self.quiz_table.c.frequency.label('frequency'),
            self.question_table.c.id.label('question_id'),
            self.question_table.c.question.label('question'),
            self.question_table.c.options.label('options'),
            self.question_table.c.right_answer.label('right_answer')
        ).select_from(query_joins).where(self.quiz_table.c.id==quiz_id, self.quiz_table.c.deleted_at==None).order_by(
            self.question_table.c.id)

        queryset = await self.db.fetch_all(query=query)

        question_count = await self.db.fetch_one(select(func.count().label('total')).select_from(
            self.question_table).where(self.question_table.c.quiz_id==quiz_id))

        if not queryset:
            raise await self.exception().quiz_not_found(id=quiz_id)
        data_in = schema_qr.QuizResponse(total_questions=question_count.total)
        return await UI_service.generate_nested_quiz(queryset=queryset, data_in=data_in)


    async def parse_quiz_result(self, income_quiz: schema_qr.IncomeQuiz, user_id: int) -> schema_qr.ResultsFeedback:
        if income_quiz.quiz_id == 0:
            raise await self.exception().id_is_0()
        quiz_questions = await self.db.fetch_all(self.question_table.select().where(self.question_table.c.quiz_id==income_quiz.quiz_id))

        quiz_serv = quiz_service.QuizResultFlow(user_id=user_id, income_quiz=income_quiz, quiz_questions=quiz_questions)
        await quiz_serv.compile_data_and_save_to_redis()
        result_data = dict(await quiz_serv.data_for_quiz_result())
         
        save_data = InsertQuizResultToDatabase(
            db=self.db, average_table=self.avarage_mark_table, quiz_results_table=self.quiz_result_table, data=result_data)

        await save_data.save_quiz_results()
        await save_data.rewrite_avg_mark()
        return schema_qr.ResultsFeedback(**result_data)


    
        
        
        
 

        
