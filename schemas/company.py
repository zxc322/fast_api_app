from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import date
from typing import List, Dict

class PublicCompany(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: date
    owner_id: int

    class Config:
        orm_mode = True

class Company(PublicCompany):
    visible: bool
    created_at: date
    updated_at: date
    


class CreateCompany(BaseModel):
    name: constr(min_length=3)
    description: Optional[constr(max_length=555)]
    visible: bool

class ResponseCompanyId(BaseModel):
    id: int


class UpdateCompany(BaseModel):
    name: Optional[constr(min_length=3)]
    description: Optional[constr(max_length=555)]
    visible: Optional[bool]

class Companies(BaseModel):
    companies: List[PublicCompany] = []
    pagination: Dict