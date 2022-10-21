from fastapi import APIRouter
import json

from schemas.user import User, UserCreate, UpdateUser, Users, UserRsposneId
from db.models import user as DBUser
from repositories.user import UserCRUD
from repositories.service import Log
from fastapi.encoders import jsonable_encoder
from utils.exceptions import CustomError


router = APIRouter()



@router.post("/", response_model=UserRsposneId, status_code=201)
async def create_user(user_in: UserCreate) :
    crud = UserCRUD(db_user=DBUser)
    
    response_user = await crud.get_by_email(email=user_in.email)
    if response_user:
        raise CustomError(user_exists=True)

    response_user = await crud.create(user_in=user_in)
    # logs
    user_data = jsonable_encoder(response_user)
    with open('logs_database.log', 'a') as f:
        f.write(Log.write_to_file_created(json.dumps(user_data)))  

    return response_user

@router.get('/{id}', response_model=User)
async def get_user_by_id(id: int) -> User:    
    crud = UserCRUD(db_user=DBUser)
    user = await crud.get_by_id(id=id)
    return user

@router.put("/{id}", response_model=UserRsposneId, status_code=201)
async def update_user(id: int, user_in: UpdateUser) -> User:
    crud = UserCRUD(db_user=DBUser)
    user = await crud.get_by_id(id=id)
    if not user:
        raise CustomError(id=id) 
    return await crud.update(id=id, user_in=user_in)

@router.delete('/{id}', response_model=UserRsposneId)
async def remove_user(id: int) -> UserRsposneId:        
    crud = UserCRUD(db_user=DBUser)
    user = await crud.get_by_id(id=id)
    if not user:
        raise CustomError(id=id)
    return await crud.remove(id=id)


@router.get("/", response_model=Users)
async def get_users_list(page: int = 1, limit: int = 10) -> Users:
    crud = UserCRUD(db_user=DBUser) 
    return await crud.get_users(page=page, limit=limit)

