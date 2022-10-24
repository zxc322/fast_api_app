from fastapi import APIRouter, Depends
import json

from schemas.user import PublicUser, User, UserCreate, UpdateUser, Users, UserRsposneId
from db.models import users as DBUser
from repositories.user import UserCRUD
from repositories.service import Log
from fastapi.encoders import jsonable_encoder
from utils.exceptions import CustomError
from utils.permissions import Permissions
from endpoints.auth import read_users_me

router = APIRouter()



@router.post("/", response_model=UserRsposneId, status_code=201)
async def create_user(user_in: UserCreate) -> UserRsposneId:
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

@router.get('/{id}', response_model=PublicUser)
async def get_user_by_id(id: int) -> PublicUser:    
    crud = UserCRUD(db_user=DBUser)
    user = await crud.get_by_id(id=id)
    return user

@router.put("/{id}", response_model=UserRsposneId, status_code=201)
async def update_user(id: int, user_in: UpdateUser, user = Depends(read_users_me)) -> UserRsposneId:
    await Permissions(user=user).permission_validator_for_user(id=id)
    crud = UserCRUD(db_user=DBUser)
    user = await crud.get_by_id(id=id)
    return await crud.update(id=id, user_in=user_in)

@router.delete('/{id}', response_model=UserRsposneId)
async def remove_user(id: int = id, user = Depends(read_users_me)) -> UserRsposneId:
    await Permissions(user=user).permission_validator_for_user(id=id)     
    crud = UserCRUD(db_user=DBUser)
    return await crud.remove(id=id)


@router.get("/", response_model=Users)
async def get_users_list(page: int = 1, limit: int = 10) -> Users:
    crud = UserCRUD(db_user=DBUser) 
    return await crud.get_users(page=page, limit=limit)

