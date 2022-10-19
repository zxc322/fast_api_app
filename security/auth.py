from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Union
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from schemas.token import TokenData
from schemas.user import User
from settings import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


async def get_current_user(crud, token: str = Depends(oauth2_scheme)) -> User:  
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    print('crud', type(crud))
    user = await crud.get_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def return_current_user(request: Request, crud):
    try:
        full_token = request.headers.get('Authorization').split(' ')
        if full_token and full_token[0] == 'Bearer':
            token = full_token[1]
            user = await get_current_user(token=token, crud=crud)
            return user
        else: raise credentials_exception
    except:
        raise credentials_exception