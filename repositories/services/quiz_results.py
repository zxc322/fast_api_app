import json

from my_redis.config import init_redis_pool
from schemas import quiz_results as schema_qr
from typing import Dict
from datetime import datetime


class QuizResultFlow:
    def __init__(self, income_quiz: schema_qr.IncomeQuiz, quiz_questions: list = [], user_id: int = None):
        self.income_quiz = income_quiz
        self.quiz_questions = quiz_questions
        self.user_id = user_id
        self.redis = init_redis_pool
        self.__total_questions = len(quiz_questions)
        self.__right_answers = 0

        
    async def compile_data_and_save_to_redis(self) -> None:
        to_redis = list()
        additional_info = [dict(total_questions=self.__total_questions)]
        await self.iterate_income_quiz_questions(questions=self.income_quiz.questions, to_redis=to_redis)        
        additional_info.append(dict(right_answers=self.__right_answers))
        await self.calculate_mark()
        additional_info.append(dict(quiz_mark=float('{:.2f}'.format(self.__mark, 2))))
        to_redis.append(additional_info)
        await self.save_to_redis(to_redis=to_redis)



    async def save_to_redis(self, to_redis: list) -> None:
        """ We are taking list with quiz results data, dump it into json and saving to redis
            (Using it in function above)
        """
        self.__quiz_id = self.quiz_questions[0].quiz_id
        to_json = json.dumps(to_redis)
        redis = await self.redis()

        await redis.hset(self.user_id, self.__quiz_id, to_json)
        await redis.expire(self.user_id, 60*60*48)


    async def calculate_mark(self) -> None:
        self.__mark = (self.__right_answers / self.__total_questions) * 10


    async def iterate_income_quiz_questions(self, questions, to_redis) -> None:
        for question in questions:
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


    async def data_for_quiz_result(self) -> schema_qr.ServiseQuizResponse:
        now = datetime.utcnow()
        return schema_qr.ServiseQuizResponse(
            total_questions=self.__total_questions,
            right_answers=self.__right_answers,
            mark=self.__mark,
            user_id=self.user_id,
            quiz_id=self.__quiz_id,
            created_at=now,
            updated_at=now
            )







