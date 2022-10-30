from db.base import Base
from pydantic import BaseModel, EmailStr, constr, root_validator
from typing import Optional
from datetime import date
from typing import List, Dict


class IncomeOption(BaseModel):
    id: int
    option_name: str
    is_right: bool

    
class IncomeQuestion(BaseModel):
    question_id: int
    chosen_option: IncomeOption


class IncomeQuiz(BaseModel):
    quiz_id: int
    questions: List[IncomeQuestion]


class ResultsFeedback(BaseModel):
    total_questions: int
    right_answers: int
    avarage_mark: float