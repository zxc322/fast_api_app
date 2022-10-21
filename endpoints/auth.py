from fastapi import APIRouter, Request
from datetime import timedelta
from fastapi import Depends
from fastapi.security import HTTPBearer

from schemas.token import Token
from schemas.user import UserRsposneId, UserSignIn, User
from security import auth 
from db.models import user as DBUser
from repositories.user import UserCRUD
from utils.exceptions import CustomError
from settings import config


token_auth_scheme = HTTPBearer()
router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: UserSignIn) -> Token:

    """ Taking email+password and generate token if data is valid or raise exepcion """

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




@router.get("/me/", response_model=UserRsposneId)
async def read_users_me(token: str = Depends(token_auth_scheme)) -> UserRsposneId:
    crud = UserCRUD(db_user=DBUser)
    return await auth.get_current_user(crud=crud, token=token)

