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
    await Permissions(user=user).validate_token()
    return await AnalitycsCRUD(db=db).my_all_quizes_avg(user_id=user.id)

@router.get('/my_avarage/quiz/{quiz_id}', response_model=schema_a.MyAvgMarkOfChosenQuizList)
async def my_results_of_chosen_quiz(quiz_id: int, user = Depends(read_users_me)):
    await Permissions(user=user).validate_token()
    return await AnalitycsCRUD(db=db).my_results_of_chosen_quiz(user_id=user.id, quiz_id=quiz_id)


@router.get('/my_latest_quizes/', response_model=schema_a.MyLatestQuizes)
async def my_quizes_latest_date(user = Depends(read_users_me)):
    await Permissions(user=user).validate_token()
    return await AnalitycsCRUD(db=db).my_quizes_latest_date(user_id=user.id)



@router.post('/member', response_model=schema_a.ChosenUserAllQuizes)
async def single_member_results(data_in: schema_a.DataIn, user = Depends(read_users_me)):
    company = await CompanyCRUD(db=db).get_by_id(id=data_in.company_id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    return await AnalitycsCRUD(db=db).single_member_results(user_id=data_in.user_id, company_id=data_in.company_id)
    


@router.get('/{company_id}', response_model=schema_a.AllMembersAvgResults)
async def avg_marks_of_chosen_company_members(company_id: int, user = Depends(read_users_me)) -> schema_a.AllMembersAvgResults:
    company = await CompanyCRUD(db=db).get_by_id(id=company_id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    return await AnalitycsCRUD(db=db).avg_marks_of_chosen_company_members(company_id=company_id)


@router.get('/comapanys_members_latest/{company_id}', response_model=schema_a.AllUsersLatestDates)
async def members_list_latest_results(company_id: int, user = Depends(read_users_me)) -> schema_a.AllUsersLatestDates:
    company = await CompanyCRUD(db=db).get_by_id(id=company_id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    return await AnalitycsCRUD(db=db).members_list_latest_results(company_id=company_id)