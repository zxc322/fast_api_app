from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import date
from typing import Union



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Union[str, None] = None