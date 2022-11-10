from schemas import analitycs as schema_a
from typing import List

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
