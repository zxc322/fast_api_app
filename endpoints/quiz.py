from fastapi import APIRouter, Depends
import json

from schemas.quiz import CompaniesQuiezes, UpdateQuestion, AppendOption, AppendQuestion, CreateQuiz, QuizResponseMessage, ResponseId, UpdateOption
from repositories.quiz import QuizCRUD
from repositories.company import CompanyCRUD
from repositories.companies_members import CompanyMemberCRUD
from db.models import companies as DBCompany, company_members as DBCompanies_members
from db.models import quiz as DBQuiz, question as DBQuestion, option as DBOption, companies as DBCompany
from endpoints.auth import read_users_me
from utils.permissions import Permissions

router = APIRouter()


@router.post('', response_model=QuizResponseMessage)
async def create_quiz(quiz: CreateQuiz, user = Depends(read_users_me)) -> QuizResponseMessage:
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=quiz.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption) 
    return await crud.create_quiz(quiz=quiz)


@router.post('/option', response_model=ResponseId)
async def append_option(option: AppendOption, user = Depends(read_users_me)) -> ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)

    # next code returns quiz_company_id joined to question (we need it for permissions)
    question = await crud.get_question_by_id(id=option.question_id)  
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=question.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)   
    return await crud.append_option(option=option)

@router.post('/change/option', response_model=ResponseId)
async def change_option(option: UpdateOption, user = Depends(read_users_me)) -> ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)
   
    # next code returns quiz_company_id joined to question (we need it for permissions)
    option_ = await crud.get_option_by_id(id=option.id)
    question = await crud.get_question_by_id(id=option_.question_id)  
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=question.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)   
    return await crud.update_option(option=option)


@router.delete('/option/{id}', response_model=ResponseId)
async def delete_option(id: int, user = Depends(read_users_me)) -> ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)

    # next code returns quiz_company_id joined to question (we need it for permissions)
    option_ = await crud.get_option_by_id(id=id)
    question = await crud.get_question_by_id(id=option_.question_id)  
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=question.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)   
    return await crud.delete_option(option=option_)


@router.post('/question', response_model=ResponseId)
async def append_question(question: AppendQuestion, user = Depends(read_users_me)) -> ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)

    # next code returns quiz_company_id joined to question (we need it for permissions)
    quiz = await crud.get_quiz_by_id(id=question.quiz_id)  
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=quiz.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)   
    return await crud.append_question(question=question)


@router.post('/change/question', response_model=ResponseId)
async def append_question(question: UpdateQuestion, user = Depends(read_users_me)) -> ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)

    # next code returns quiz_company_id joined to question (we need it for permissions)
    question_ = await crud.get_question_by_id(id=question.id)   
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=question_.company_id)     
    await Permissions(user=user).permission_validator_for_company_owner(company=company)   
    return await crud.update_question(question=question)


@router.delete('/question/{id}')#, response_model=ResponseId)
async def delete_option(id: int, user = Depends(read_users_me)) -> ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)

    # next code returns quiz_company_id joined to question (we need it for permissions)
    question_ = await crud.get_question_by_id(id=id)   
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=question_.company_id)     
    await Permissions(user=user).permission_validator_for_company_owner(company=company)     
    return await crud.delete_question(question=question_)


@router.get('/company/{id}', response_model=CompaniesQuiezes)
async def delete_option(id: int, page: int = 1, limit: int = 10) -> CompaniesQuiezes:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)         
    return await crud.get_quiz_list(company_id=id, page=page, limit=limit)