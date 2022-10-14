from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi_pagination  import Page, LimitOffsetPage, paginate, add_pagination

from db.base import get_db
from schemas.user import User, UserCreate, UpdateUser
from db.models import User as DBUser
from repositories import user as crud_user


router = APIRouter()

@router.post("/", response_model=User, status_code=201)
def create_user(db: Session = Depends(get_db), *, user_in: UserCreate) -> User:
    response_user = crud_user.get_by_email(db, email=user_in.email)
    if response_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    response_user = crud_user.create(db, user_in=user_in)
    return response_user

@router.get('/{id}', response_model=User)
def get_user_by_id(db: Session = Depends(get_db), *, id: int) -> User:    
    user = crud_user.get_by_id(db, id=id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with id {} doesn't exists.".format(id),
        )
    return user

@router.put("/{id}", response_model=User, status_code=201)
def update_user(db: Session = Depends(get_db), *,  id: int, user_in: UpdateUser) -> User:
    user = crud_user.get_by_id(db, id=id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with id {} doesn't exists.".format(id),
        ) 
    user = crud_user.update(db, user, user_in)
    return user

@router.delete('/{id}', response_model=User)
def remove_user(db: Session = Depends(get_db), *, id: int) -> User:    
    user = crud_user.remove(db, id=id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with id {} doesn't exists.".format(id),
        )
    return user

@router.get('/', response_model=Page[User])
@router.get('limit-offset', response_model=LimitOffsetPage[User])
def get_users(db: Session = Depends(get_db)):
    return paginate(db.query(DBUser).all())

add_pagination(router)