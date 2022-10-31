from fastapi import APIRouter, Depends

from schemas.company import CreateCompany, ResponseCompanyId, UpdateCompany, Companies
from repositories.company import CompanyCRUD
from utils.exceptions import CustomError
from utils.permissions import Permissions
from endpoints.auth import read_users_me
from db.connection import database as db

router = APIRouter()



@router.post("/", response_model=ResponseCompanyId, status_code=201)
async def create_company(company_in: CreateCompany, user = Depends(read_users_me)) -> ResponseCompanyId:
    await Permissions(user=user).validate_token()
    crud = CompanyCRUD(db=db)   
    if await crud.get_by_name(name=company_in.name):
        raise CustomError(company_exists=True) 
    return await crud.create(company_in=company_in, owner=user.id)


@router.put("/{id}", response_model=ResponseCompanyId, status_code=201)
async def update_company(id: int, company_in: UpdateCompany, user = Depends(read_users_me)) -> ResponseCompanyId:
    crud = CompanyCRUD(db=db)
    company = await crud.get_by_id(id=id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)    
    return await crud.update(id=id, company_in=company_in)


@router.delete('/{id}', response_model=ResponseCompanyId)
async def remove_company(id: int = id, user = Depends(read_users_me)) -> ResponseCompanyId:
    crud = CompanyCRUD(db=db)
    company = await crud.get_by_id(id=id)
    await Permissions(user=user).permission_validator_for_company_owner(company=company)
    return await crud.remove(id=id)


@router.get("/", response_model=Companies)
async def get_companies_list(page: int = 1, limit: int = 10) -> Companies:
    crud = CompanyCRUD(db=db)
    return await crud.get_companies(page=page, limit=limit)