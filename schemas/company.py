from pydantic import BaseModel, constr
from typing import Optional
from datetime import date
from typing import List, Dict

from schemas import generic


class ReturnCompany(generic.ResponseId):
    name: str
    description: Optional[str]
    visible: bool
    created_at: date
    updated_at: date
    owner_id: int

class PublicCompany(BaseModel):
    company_id: int
    company_name: str
    description: Optional[str]
    created_at: date
    owner_id: int
    owner_usename: str

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


class UpdateCompany(BaseModel):
    name: Optional[constr(min_length=3)]
    description: Optional[constr(max_length=555)]
    visible: Optional[bool]

class Companies(BaseModel):
    companies: List[PublicCompany] = []
    pagination: Dict


class ResponseCompanyId(generic.ResponseId):
    pass