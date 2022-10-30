from fastapi import APIRouter, Depends
# import UpdateQuiz, CompaniesQuiezes, UpdateQuestion, AppendOption, AppendQuestion, CreateQuiz, QuizResponseMessage, ResponseId, UpdateOption
from schemas import quiz as  schema_q
from schemas import quiz_results as  schema_qr
from repositories.quiz import QuizCRUD
from repositories.company import CompanyCRUD
from db.models import quiz as DBQuiz, question as DBQuestion, option as DBOption, companies as DBCompany, quiz_result, avarage_mark
from endpoints.auth import read_users_me
from utils.permissions import Permissions
from repositories.quiz_results import QuizResultCRUD

router = APIRouter()


@router.post('', response_model=schema_q.QuizResponseMessage)
async def create_quiz(quiz: schema_q.CreateQuiz, user = Depends(read_users_me)) -> schema_q.QuizResponseMessage:
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=quiz.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption) 
    return await crud.create_quiz(quiz=quiz)


@router.post('/option', response_model=schema_q.ResponseId)
async def append_option(option: schema_q.AppendOption, user = Depends(read_users_me)) -> schema_q.ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)

    # next code returns quiz_company_id joined to question (we need it for permissions)
    question = await crud.get_question_by_id(id=option.question_id)  
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=question.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)   
    return await crud.append_option(option=option)

@router.post('/change/option', response_model=schema_q.ResponseId)
async def change_option(option: schema_q.UpdateOption, user = Depends(read_users_me)) -> schema_q.ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)
   
    # next code returns quiz_company_id joined to question (we need it for permissions)
    option_ = await crud.get_option_by_id(id=option.id)
    question = await crud.get_question_by_id(id=option_.question_id)  
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=question.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)   
    return await crud.update_option(option=option)


@router.delete('/option/{id}', response_model=schema_q.ResponseId)
async def delete_option(id: int, user = Depends(read_users_me)) -> schema_q.ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)

    # next code returns quiz_company_id joined to question (we need it for permissions)
    option_ = await crud.get_option_by_id(id=id)
    question = await crud.get_question_by_id(id=option_.question_id)  
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=question.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)   
    return await crud.delete_option(option=option_)


@router.post('/question', response_model=schema_q.ResponseId)
async def append_question(question: schema_q.AppendQuestion, user = Depends(read_users_me)) -> schema_q.ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)

    # next code returns quiz_company_id joined to question (we need it for permissions)
    quiz = await crud.get_quiz_by_id(id=question.quiz_id)  
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=quiz.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)   
    return await crud.append_question(question=question)


@router.post('/change/question', response_model=schema_q.ResponseId)
async def append_question(question: schema_q.UpdateQuestion, user = Depends(read_users_me)) ->schema_q.ResponseId:
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)

    # next code returns quiz_company_id joined to question (we need it for permissions)
    question_ = await crud.get_question_by_id(id=question.id)   
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=question_.company_id)     
    await Permissions(user=user).permission_validator_for_company_owner(company=company)   
    return await crud.update_question(question=question)


@router.delete('/question/{id}', response_model=schema_q.ResponseId)
async def delete_option(id: int, user = Depends(read_users_me)) -> schema_q.ResponseId:
    """ Delete option from question, where option.question_id==id (Raise exc if len(options) of this question <=2 """
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)

    # next code returns quiz_company_id joined to question (we need it for permissions)
    question_ = await crud.get_question_by_id(id=id)   
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=question_.company_id)     
    await Permissions(user=user).permission_validator_for_company_owner(company=company)     
    return await crud.delete_question(question=question_)


@router.get('/company/{id}', response_model=schema_q.CompaniesQuiezes)
async def delete_option(id: int, page: int = 1, limit: int = 10) -> schema_q.CompaniesQuiezes:
    """ Returns a list of quizes, where quiz.company_id==id"""

    # Idk do we need permissions here? Will add it later if yes ...
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)         
    return await crud.get_quiz_list(company_id=id, page=page, limit=limit)


@router.post('/update')
async def update_quiz(quiz: schema_q.UpdateQuiz, user = Depends(read_users_me)) -> schema_q.ResponseId:
    """ Updates quiz attributes (but not nested fields) """
    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)
    quiz_ = await crud.get_quiz_by_id(id=quiz.id)
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=quiz_.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    return await crud.update_quiz(quiz=quiz)


@router.delete('/{id}', response_model=schema_q.ResponseId)
async def delete_option(id: int, user = Depends(read_users_me)) -> schema_q.ResponseId:
    """ This endpoint fill "deleted_at" field (we are using it for filter) """

    crud = QuizCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption)
    quiz_ = await crud.get_quiz_by_id(id=id)
    company = await CompanyCRUD(db_company=DBCompany).get_by_id(id=quiz_.company_id)    
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    
    return await crud.remove_quiz(id=id)


@router.get('/{id}', response_model=schema_q.QuizForUser)
async def get_quiz(quiz_id: int) -> schema_q.QuizForUser:
    """ Returns full quiz (with nested questions and options) by quiz_id """

    crud = QuizResultCRUD(db_quiz=DBQuiz, db_question=DBQuestion, db_option=DBOption, db_quiz_result=quiz_result, db_avarage_mark=avarage_mark)                
    return await crud.get_ui_quiz(quiz_id=quiz_id)