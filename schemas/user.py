from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import date
from typing import List, Dict

from schemas import generic

class UserRsposneId(generic.ResponseId):
    pass

class PublicUser(generic.ResponseId):
    username: str
    about_me: Optional[str]
    is_active: bool
    created_at: date

    class Config:
        orm_mode = True

class User(PublicUser):
    email: EmailStr
    password: str
    is_admin: bool
    updated_at: date
    updated_by: Optional[int]


class UserCreate(BaseModel):
    username: constr(min_length=3)
    email: EmailStr
    password1: constr(min_length=3)
    password2: str
    about_me: Optional[str] = None

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError('passwords do not match')
        return v


class UpdateUser(BaseModel):
    username: Optional[constr(min_length=3)]
    password: Optional[constr(min_length=3)]
    about_me: Optional[str]


class Users(BaseModel):
    users: List[PublicUser] = []
    pagination: Dict


class UserSignIn(BaseModel):
    email: EmailStr
    password: str

    
class ResponseUserDataFromToken(generic.ResponseId):
    is_admin: bool


class IsUserAdmin(UserSignIn, ResponseUserDataFromToken):
    pass
    




