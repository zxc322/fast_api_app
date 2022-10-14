from ssl import _PasswordType
from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import date


class BaseUser(BaseModel):    
    username: str

class User(BaseUser):
    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: date
    updated_at: date
    # updated_by: BaseUser

    class Config:
        orm_mode = True


class UserCreate(BaseUser):
    email: EmailStr
    password1: constr(min_length=3)
    password2: str

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError('passwords do not match')
        return v

class UserSignIn(BaseUser):
    password: str
    

class UpdateUser(BaseUser):
    is_active: Optional[bool] = False
    is_admin: Optional[bool] = False
    updated_by: User

    class Config:
        orm_mode = True





