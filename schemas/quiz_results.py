from db.base import Base
from pydantic import BaseModel, EmailStr, constr, root_validator
from typing import Optional
from datetime import date
from typing import List, Dict

    
class IncomeQuestion(BaseModel):
    question_id: int
    question: str
    chosen_option: str


class IncomeQuiz(BaseModel):
    quiz_id: int
    questions: List[IncomeQuestion]


class ResultsFeedback(BaseModel):
    total_questions: int
    right_answers: int
    mark: float


class QuizResponse(BaseModel):
    quiz_id: Optional[int]
    quiz_name: Optional[str]
    frequency: Optional[int]
    total_questions: Optional[int]
    questions: Optional[List] = []


class ServiseQuizResponse(ResultsFeedback):
    user_id: int
    quiz_id: int
    created_at: date
    updated_at: date