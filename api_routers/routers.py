from fastapi import APIRouter

from endpoints import user, auth, company, companies_members, quiz, quiz_results, export, analitycs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(quiz_results.router, prefix="/quiz_results", tags=["quiz_results"])
api_router.include_router(companies_members.router, prefix="/company_members", tags=["company_members"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(analitycs.router, prefix="/analitycs", tags=["analitycs"])

