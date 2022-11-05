from schemas import quiz_results as schema_qr
from schemas import quiz as schema_q
async def generate_nested_quiz(queryset, data_in: schema_qr.QuizResponse) -> schema_q.QuizForUser:
        """ Generate a dict with all nested fields of quiz """

        quiz_response=dict(data_in)
 
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