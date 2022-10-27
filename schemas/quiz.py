from db.base import Base
from pydantic import BaseModel, EmailStr, constr, root_validator
from typing import Optional
from datetime import date
from typing import List, Dict


class ResponseId(BaseModel):
    id: int


class Options(BaseModel):
    option: str
    is_right: bool = False

class AppendOption(Options):
    question_id: int

class UpdateOption(BaseModel):
    id: int
    option: Optional[str]
    is_right: Optional[bool]

class FullOptionData(ResponseId, AppendOption):
    pass

class Question(BaseModel):
    question: str
    options: List[Options]
    
    @root_validator
    def check_options_length(cls, values):
        options = values.get('options')
        if not options or len(options) < 2:
            raise ValueError('Minimum 2 options for question required')
        return values


class AppendQuestion(Question):
    quiz_id: int



class ReturnQuestion(BaseModel):
    id: int
    question: str
    quiz_id: int
    company_id: int 



class CreateQuiz(BaseModel):
    company_id: int
    name: str
    description: str
    frequency: int
    questions: List[Question]

    @root_validator
    def check_questions_length(cls, values):
        questions = values.get('questions')
        if not questions or len(questions) < 2:
            raise ValueError('Minimum 2 questions for quiz required')
        return values


class CheckQuiz(BaseModel):
    id: int
    name: str

class QuizResponseMessage(BaseModel):
    message: str


class PublickQuiz(BaseModel):
    id: int
    name: str
    description: str


class CompaniesQuiezes(BaseModel):
    quizes: List[PublickQuiz] = []
    pagination: Dict


class FullQuizInfo(PublickQuiz):
    created_at: date
    updated_at: date
    company_id: int

class UpdateQuestion(BaseModel):
    id: int
    question: str

