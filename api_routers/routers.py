from fastapi import APIRouter

from endpoints import user, auth, company, companies_members, quiz

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(companies_members.router, prefix="/company_members", tags=["company_members"])

