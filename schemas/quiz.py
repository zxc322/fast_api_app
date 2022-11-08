from pydantic import BaseModel, root_validator
from typing import Optional
from datetime import date
from typing import List, Dict

from schemas import generic


class ResponseId(generic.ResponseId):
    pass


class Option(BaseModel):
    options: List[str]

class AppendOption(Option):
    question_id: int

class DeleteOptionByName(BaseModel):
    question_id: int
    name: str

class OtionForUser(Option):
    option_id: int

class Question(BaseModel):
    question: str
    right_answer: int
    options: List[str]
    
    
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


class CheckQuiz(generic.ResponseId):
    name: str

class QuizResponseMessage(BaseModel):
    message: str


class PublickQuiz(generic.ResponseId):
    name: str
    description: Optional[str]


class CompaniesQuiezes(BaseModel):
    quizes: List[PublickQuiz] = []
    pagination: Dict


class FullQuizInfo(PublickQuiz):
    created_at: date
    updated_at: date
    company_id: int

class UpdateQuestion(generic.ResponseId):
    question: Optional[str]
    options: Optional[List[str]]
    right_answer: Optional[int]

    @root_validator
    def check_questions_length(cls, values):
        questions = values.get('options')
        if questions and len(questions) < 2:
            raise ValueError('Minimum 2 options for question required')
        return values

class UpdateQuiz(generic.ResponseId):
    name: Optional[str]
    description: Optional[str]
    frequency: Optional[int]

class OtionForUser(Option): 
    option_id: int

class QuestionForUser(BaseModel):
    question_id: int
    question: str
    right_answer: int
    options: List[str]

class QuizForUser(BaseModel):
    quiz_id: int
    quiz_name: str
    frequency: int
    total_questions: int
    questions: List[QuestionForUser]

