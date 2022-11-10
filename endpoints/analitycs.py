from fastapi import APIRouter, Depends

from schemas import analitycs as schema_a
from repositories.analytics import AnalitycsCRUD
from repositories.company import CompanyCRUD
from utils.permissions import Permissions
from endpoints.auth import read_users_me
from db.connection import database as db

router = APIRouter()


@router.get('/my_avarage', response_model=schema_a.MyAvgMark)
async def my_all_quizes_avg(user = Depends(read_users_me)) -> schema_a.MyAvgMark:
    return await AnalitycsCRUD(db=db).my_all_quizes_avg(user_id=user.id)


@router.post('/member', response_model=schema_a.ChosenUserAllQuizes)
async def single_member_results(data_in: schema_a.DataIn):
    return await AnalitycsCRUD(db=db).single_member_results(user_id=data_in.user_id, company_id=data_in.company_id)
    




@router.get('/{quiz_id}')
async def avg_marks_by_quiz_id(quiz_id: int, ):
    return await AnalitycsCRUD(db=db).avg_marks_by_quiz_id(quiz_id=quiz_id, company_id=3)