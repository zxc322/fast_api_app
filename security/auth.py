from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Union
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from schemas.token import TokenData
from schemas.user import User, UserRsposneId
from settings import config
from security.auth0 import VerifyToken
from utils.exceptions import MyExceptions# credentials_exception

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")



def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt



async def get_current_user(crud, token) -> UserRsposneId:

    """ First try to decode token with 'HS256'. If success get user by email and return users id
        If error try to decode with 'RS256'(VerifyToken instanse). 
        instanse.verify() returns id or raise error"""
     
    try:
        payload = jwt.decode(token.credentials, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise await MyExceptions().credentials_exception()
        token_data = TokenData(email=email)
    except JWTError:
        #raise credentials_exception
        try:
            instanse = VerifyToken(token.credentials, crud=crud)
            result = await instanse.verify()
            return result
        except:
            raise await MyExceptions().credentials_exception()
    user = await crud.get_by_email(email=token_data.email)
    if user is None:
        raise await MyExceptions().credentials_exception()
    return UserRsposneId(id=user.id)

