from fastapi import APIRouter, Request
from datetime import datetime, timedelta

from schemas.token import Token
from schemas.user import UserSignIn, User
from security import auth 
from db.models import user as DBUser
from repositories.user import UserCRUD
from utils.exceptions import CustomError
from settings import config


router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: UserSignIn) -> Token:
    crud = UserCRUD(db_user=DBUser)
    user = await crud.get_by_email(email=form_data.email)
    if not user:
        raise CustomError(email=form_data.email)
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    if not auth.verify_password(form_data.password, user.password):
        raise CustomError(wrong_password=True)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(**{"access_token": access_token, "token_type": "bearer"})

@router.get("/me/", response_model=User)
async def read_users_me(request: Request) -> User:
    crud = UserCRUD(db_user=DBUser)
    return await auth.return_current_user(crud=crud, request=request)