from fastapi import APIRouter, Depends



from repositories.quiz_results import QuizResultCRUD
from db.models import quiz as DBQuiz, question as DBQuestion, option as DBOption, companies as DBCompany, quiz_result, avarage_mark
from endpoints.auth import read_users_me
from utils.permissions import Permissions
from schemas import quiz_results as schema_qr

router = APIRouter()

@router.post('/', response_model=schema_qr.ResultsFeedback)
async def send_quiz_results(income_quiz: schema_qr.IncomeQuiz, user = Depends(read_users_me)):
    await Permissions(user=user).validate_token()
    crud = QuizResultCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption, db_quiz_result=quiz_result, db_avarage_mark=avarage_mark)         
    return await crud.parse_quiz_result(income_quiz=income_quiz, user_id=user.id)