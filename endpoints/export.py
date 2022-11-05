from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
import os

from endpoints.auth import read_users_me
from my_redis.export import Export
from utils.exceptions import MyExceptions
from utils.permissions import Permissions
from schemas import export as schema_e
from repositories.company import CompanyCRUD
from repositories.quiz import QuizCRUD
from repositories.companies_members import CompanyMemberCRUD
from db.connection import database as db


router = APIRouter()

path = os.getcwd()


@router.get("/my_results", status_code=200)
async def export_my_results(user = Depends(read_users_me)):    
    await Permissions(user=user).validate_token()
    await Export().create_my_results_csv(user_id=user.id)

    file_path = os.path.join(path, 'export_data/my_result.csv')
    if not os.path.exists(file_path):
        raise await MyExceptions.data_was_not_found()
    return FileResponse(file_path, media_type='text/csv', filename='my_result.csv')
    

@router.post("/single_member_results", status_code=200)
async def get_single_members_results(data: schema_e.ExportUsersResults, user = Depends(read_users_me)):
    company = await CompanyCRUD(db=db).get_by_id(id=data.company_id)
    await Permissions(user=user).read_users_results(user_id=data.user_id, company=company)
    quiz_ids = await QuizCRUD(db=db).get_quiz_ids_list_for_redis(company_id=data.company_id)
    await Export().create_company_member_csv(member_id=data.user_id, companies_quizes_ids=quiz_ids)

    file_path = os.path.join(path, 'export_data/members_result.csv')
    if not os.path.exists(file_path):
        raise await MyExceptions.data_was_not_found()
    return FileResponse(file_path, media_type='text/csv', filename='members_result.csv')


@router.post("/all_members_results", status_code=200)
async def get_all_members_results(data: schema_e.CompanyId, user = Depends(read_users_me)):
    company = await CompanyCRUD(db=db).get_by_id(id=data.company_id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    quiz_ids = await QuizCRUD(db=db).get_quiz_ids_list_for_redis(company_id=data.company_id)
    members_ids = await CompanyMemberCRUD(db=db).membres_of_chosen_company(company_id=data.company_id)

    filename = 'export_data/all_members_result.csv'
    await Export().create_all_members_csv(members_ids=members_ids, companies_quizes_ids=quiz_ids, filename=filename)

    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        raise await MyExceptions.data_was_not_found()
    return FileResponse(file_path, media_type='text/csv', filename='all_members_result.csv')


@router.post("/quiz_results", status_code=200)
async def get_quiz_results(data: schema_e.ExportByQuizId, user = Depends(read_users_me)):
    company = await CompanyCRUD(db=db).get_by_id(id=data.company_id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    members_ids = await CompanyMemberCRUD(db=db).membres_of_chosen_company(company_id=data.company_id)

    filename = 'export_data/quiz_result.csv'
    await Export().create_all_members_csv(members_ids=members_ids, companies_quizes_ids=[data.quiz_id], filename=filename)

    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        raise await MyExceptions.data_was_not_found()
    return FileResponse(file_path, media_type='text/csv', filename='quiz_result.csv')


