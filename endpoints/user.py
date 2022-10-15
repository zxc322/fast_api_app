from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

from db.base import get_db
from schemas.user import User, UserCreate, UpdateUser, Users
from db.models import User as DBUser
from repositories.user import UserCRUD
from repositories.service import Log
from fastapi.encoders import jsonable_encoder
from utils.exceptions import CustomError


router = APIRouter()



@router.post("/", response_model=User, status_code=201)
def create_user(db: Session = Depends(get_db), *, user_in: UserCreate) -> User:
    response_user = UserCRUD.get_by_email(db, email=user_in.email)
    if response_user:
        raise CustomError()
    response_user = UserCRUD.create(db, user_in=user_in)
    
    user_data = jsonable_encoder(response_user)
    with open('logs_database.log', 'a') as f:
        f.write(Log.write_to_file_created(json.dumps(user_data)))  
    return response_user

@router.get('/{id}', response_model=User)
def get_user_by_id(db: Session = Depends(get_db), *, id: int) -> User:    
    user = UserCRUD.get_by_id(db, id=id)
    if not user:
        raise CustomError(id=id)
    return user

@router.put("/{id}", response_model=User, status_code=201)
def update_user(db: Session = Depends(get_db), *,  id: int, user_in: UpdateUser) -> User:
    user = UserCRUD.get_by_id(db, id=id)
    if not user:
        raise CustomError(id=id) 
    user = UserCRUD.update(db, user, user_in)
    return user

@router.delete('/{id}', response_model=User)
def remove_user(db: Session = Depends(get_db), *, id: int) -> User:        
    user = UserCRUD.remove(db, id=id)
    if not user:
        raise CustomError(id=id)
    return user


@router.get("/", response_model=Users)
async def get_users_list(page: int = 1, limit: int = 10, db: Session = Depends(get_db)) -> Users:
    response = UserCRUD.get_users(db, page=page, limit=limit) 
    return Users(**response)

