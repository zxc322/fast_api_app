import json

from my_redis.config import init_redis_pool
from schemas import quiz_results as schema_qr
from typing import Dict
from datetime import datetime
from db.connection import database
from schemas import quiz as schema_q

class QuizResultFlow:
    def __init__(self, income_quiz: schema_qr.IncomeQuiz, quiz_questions: list = [], user_id: int = None):
        self.income_quiz = income_quiz
        self.quiz_questions = quiz_questions
        self.user_id = user_id
        self.redis = init_redis_pool
        self.__total_questions = len(quiz_questions)
        self.__right_answers = 0
        
    async def generate_dict_for_redis(self):
        to_redis = [dict(total_questions=self.__total_questions)]

        for question in self.income_quiz.questions:
            dict_question = dict(
                id=question.question_id,
                question=question.question,
                answer=question.chosen_option
                )
                        
            for q in self.quiz_questions:
                if q.id==question.question_id:
                    try:
                        idx = q.options.index(question.chosen_option)
                    except ValueError: # If chosen option not in batabase options
                        idx = None
                    dict_question['is_right'] = idx==q.right_answer
                    self.__right_answers += 1 if dict_question.get('is_right') else 0

            to_redis.append(dict_question)

        to_redis.append(dict(right_answers=self.__right_answers))

        await self.calculate_mark()
        to_redis.append(dict(quiz_mark=float('{:.2f}'.format(self.__mark, 2))))

        await self.save_to_redis(to_redis=to_redis)



    async def save_to_redis(self, to_redis):
        self.__quiz_id = self.quiz_questions[0].quiz_id
        quiz_id = 'quiz_id_' + str(self.__quiz_id)
        to_json = json.dumps(to_redis)
        redis = await self.redis()

        await redis.hset(self.user_id, quiz_id, to_json)
        await redis.expire(self.user_id, 60*60*48)


    async def calculate_mark(self):
        self.__mark = (self.__right_answers / self.__total_questions) * 10


    async def data_for_quiz_result(self) -> dict:
        return dict(
            total_questions=self.__total_questions,
            right_answers=self.__right_answers,
            mark=self.__mark,
            user_id=self.user_id,
            quiz_id=self.__quiz_id
            )




async def generate_nested_quiz(queryset, data_in: schema_qr.QuizResponse) -> schema_q.QuizForUser:
        """ Generate a dict with all nested fields of quiz """

        quiz_response=dict(data_in)
        for a in queryset:
            print(dict(a), end='\n')
 
        for question in queryset:
            if not quiz_response.get('quiz_id'):
                quiz_response['quiz_id'] = question.quiz_id
            if not quiz_response.get('quiz_name'):
                quiz_response['quiz_name'] = question.quiz_name
            if not quiz_response.get('frequency'):
                quiz_response['frequency'] = question.quiz_id

            new_question = dict(
                question_id=question.question_id, 
                question=question.question, 
                right_answer=question.right_answer,
                options = question.options)
            quiz_response.get('questions').append(new_question)

        return schema_q.QuizForUser(**quiz_response)


async def rewrite_avg_mark(average_table, data: Dict):
        del data['quiz_id']
        
        user_data = await database.fetch_one(average_table.select().where(average_table.c.user_id==data.get('user_id')))
        if not user_data:      
            data['quizzes_passed'] = 1
            data['avarage_mark'] = data.pop('mark')
            return await database.execute(average_table.insert().values(data))
        updated_data = dict()
        updated_data['quizzes_passed'] = user_data.quizzes_passed + 1
        updated_data['total_questions'] = user_data.total_questions + data.get('total_questions')
        updated_data['right_answers'] = user_data.right_answers + data.get('right_answers')
        updated_data['avarage_mark'] =  (updated_data.get('right_answers') / updated_data.get('total_questions')) *10
        updated_data['updated_at'] = datetime.utcnow()
        return await database.execute(average_table.update().values(updated_data).where(average_table.c.user_id==data.get('user_id')))
