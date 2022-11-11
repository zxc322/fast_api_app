from typing import List

from schemas import analitycs as schema_a


async def complete_results(data: List) -> schema_a.ChosenUserAllQuizes:
    result = list()
    quiz_ids_set = set(i.quiz_id for i in data)
    
    for quiz_id in quiz_ids_set:
        result.append(dict(quiz_id=quiz_id, quiz_details=list()))

    for d in data:
        for r in result:
            if d.quiz_id == r.get('quiz_id'):
                data = dict(d)
                data.pop('quiz_id')
                r.get('quiz_details').append(data)

    return schema_a.ChosenUserAllQuizes(results=result)


async def complete_pretty_dict(results: List, response: List) -> None:
    for record in results:
            for res in response:
                if record.user_id == res.get('user_id'):
                    quizes = [x.get('quiz_id') for x in res.get('quiz_data')]
                    if record.quiz_id not in quizes:
                        res.get('quiz_data').append(dict(
                            quiz_id=record.quiz_id, details=[dict(
                                date=record.date,
                                total_questions=record.total_questions,
                                right_answers=record.right_answers,
                                mark=record.mark)]))
                    else:

                        for quiz in res.get('quiz_data'):
                            if quiz.get('quiz_id') == record.quiz_id:
                                quiz.get('details').append(dict(
                                        date=record.date,
                                        total_questions=record.total_questions,
                                        right_answers=record.right_answers,
                                        mark=record.mark))