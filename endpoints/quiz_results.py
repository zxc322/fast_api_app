from fastapi import APIRouter, Depends



from repositories.quiz_results import QuizResultCRUD
from repositories.quiz import QuizCRUD
from endpoints.auth import read_users_me
from utils.permissions import Permissions
from schemas import quiz_results as schema_qr
from db.connection import database as db

router = APIRouter()

@router.post('/', response_model=schema_qr.ResultsFeedback)
async def send_quiz_results(income_quiz: schema_qr.IncomeQuiz, user = Depends(read_users_me)):
    # Chek if quiz exists or raise exc
    await QuizCRUD(db=db).get_quiz_by_id(id=income_quiz.quiz_id)

    await Permissions(user=user).validate_token()
    crud = QuizResultCRUD(db=db)         
    return await crud.parse_quiz_result(income_quiz=income_quiz, user_id=user.id)