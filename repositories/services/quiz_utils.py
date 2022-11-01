from typing import Dict
from datetime import datetime

from db.connection import database
from schemas import quiz_results as schema_qr
from schemas import quiz as schema_q

# async def generate_nested_quiz(queryset, question_count) -> Dict:
async def generate_nested_quiz(queryset, data_in: schema_qr.QuizResponse) -> Dict:
        """ Generate a dict with all nested fields of quiz """

        quiz_response=dict(data_in)
 
        for s in queryset:
            if not quiz_response.get('quiz_id'):
                quiz_response['quiz_id'] = s.quiz_id
            if not quiz_response.get('quiz_name'):
                quiz_response['quiz_name'] = s.quiz_name
            if not quiz_response.get('frequency'):
                quiz_response['frequency'] = s.quiz_id


            # add question to question list if not exists
            if s.question_id not in (x.get('question_id') for x  in quiz_response.get('questions')):
                quiz_response.get('questions').append(dict(question_id=s.question_id, question=s.question, options=list()))

            # add option to related question
            for question in quiz_response.get('questions'):
                if s.option_question_id == question.get('question_id'):
                    question.get('options').append(dict(option_id=s.option_id, option=s.option, is_right=s.is_right))

        return schema_q.QuizForUser(**quiz_response)


async def generate_users_results_as_dict(user_id: int, income_quiz) -> Dict:
    now = datetime.utcnow()
    result = dict(user_id=user_id, quiz_id=income_quiz.quiz_id, total_questions=len(income_quiz.questions), created_at=now, updated_at=now)
    
    right_answers = 0
    for question in income_quiz.questions:
        right_answers += 1 if question.chosen_option.is_right==True else 0
    result['right_answers'] = right_answers
    result['avarage_mark'] =  (right_answers / result.get('total_questions')) * 10
    return result


async def rewrite_avg_mark(average_table, data: Dict):
        del data['quiz_id']
        
        user_data = await database.fetch_one(average_table.select().where(average_table.c.user_id==data.get('user_id')))
        if not user_data:      
            data['quizzes_passed'] = 1
            return await database.execute(average_table.insert().values(data))
        updated_data = dict()
        updated_data['quizzes_passed'] = user_data.quizzes_passed + 1
        updated_data['total_questions'] = user_data.total_questions + data.get('total_questions')
        updated_data['right_answers'] = user_data.right_answers + data.get('right_answers')
        updated_data['avarage_mark'] =  (updated_data.get('right_answers') / updated_data.get('total_questions')) *10
        updated_data['updated_at'] = datetime.utcnow()
        return await database.execute(average_table.update().values(updated_data).where(average_table.c.user_id==data.get('user_id')))
