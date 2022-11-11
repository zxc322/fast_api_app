from fastapi import APIRouter, Depends
import json

from schemas import user as schemas_u 
from repositories.user import UserCRUD
from repositories.services.log import Log
from fastapi.encoders import jsonable_encoder
from utils.exceptions import CustomError
from utils.permissions import Permissions
from endpoints.auth import read_users_me
from db.connection import database as db

router = APIRouter()



@router.post("/", response_model=schemas_u.UserRsposneId, status_code=201)
async def create_user(user_in: schemas_u.UserCreate) -> schemas_u.UserRsposneId:
    crud = UserCRUD(db=db)
    
    response_user = await crud.get_by_email(email=user_in.email)
    if response_user:
        raise CustomError(user_exists=True)

    response_user = await crud.create(user_in=user_in)
    # logs
    user_data = jsonable_encoder(response_user)
    with open('logs_database.log', 'a') as f:
        f.write(Log.write_to_file_created(json.dumps(user_data)))  

    return response_user

@router.get('/{id}', response_model=schemas_u.PublicUser)
async def get_user_by_id(id: int) -> schemas_u.PublicUser:    
    crud = UserCRUD(db=db)
    user = await crud.get_by_id(id=id)
    return user

@router.put("/{id}", response_model=schemas_u.UserRsposneId, status_code=201)
async def update_user(id: int, user_in: schemas_u.UpdateUser, user = Depends(read_users_me)) -> schemas_u.UserRsposneId:
    await Permissions(user=user).permission_validator_for_user(id=id)
    crud = UserCRUD(db=db)
    user = await crud.get_by_id(id=id)
    return await crud.update(id=id, user_in=user_in, updated_by=user.id)

@router.delete('/{id}', response_model=schemas_u.UserRsposneId)
async def remove_user(id: int = id, user = Depends(read_users_me)) -> schemas_u.UserRsposneId:
    await Permissions(user=user).permission_validator_for_user(id=id)     
    crud = UserCRUD(db=db)
    return await crud.remove(id=id)


@router.get("/", response_model=schemas_u.Users)
async def get_users_list(page: int = 1, limit: int = 10) -> schemas_u.Users:
    crud = UserCRUD(db=db)
    return await crud.get_users(page=page, limit=limit)

