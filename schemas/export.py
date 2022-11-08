from pydantic import BaseModel

from schemas.companies_members import Invite



class ExportUsersResults(Invite):
    pass

class CompanyId(BaseModel):
    company_id: int

class ExportByQuizId(CompanyId):
    quiz_id: int