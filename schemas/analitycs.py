from pydantic import BaseModel
from typing import List
from datetime import date, datetime


class DataIn(BaseModel):
    user_id: int
    company_id: int


class UsersResults(BaseModel):
    mark: float
    date: date


class UsersMarksByQuizId(BaseModel):
    user_id: int
    results: UsersResults

class AllUsersMarksByQuizId(BaseModel):
    quiz_id: int
    results: List[UsersMarksByQuizId]


class QuizDetails(BaseModel):
    total_questions: int
    right_answers: int
    mark: int
    date: date


class SingleUserQuizes(BaseModel):
    quiz_id: int
    quiz_details: List[QuizDetails]
    

class ChosenUserAllQuizes(BaseModel):
    results: List[SingleUserQuizes]


class QuizInfo(BaseModel):
    quiz_id: int
    last_time_result: date

class Member(BaseModel):
    id: int
    quizes: List[QuizInfo]

class CompanysMembersInfo(BaseModel):
    members: List[Member]


class MyAvgMark(BaseModel):
    quizzes_passed: int
    total_questions: int
    right_answers: int
    avarage_mark: int


class MyAvgMarkOfChosenQuiz(BaseModel):
    total_questions: int
    right_answers: int
    mark: float
    date: datetime


class MyAvgMarkOfChosenQuizList(BaseModel):
    my_results: List[MyAvgMarkOfChosenQuiz] = []


class LatestQuizData(BaseModel):
    quiz_id: int
    date: date

class LatestUsersResults(BaseModel):
    user_id: int
    quiz_data: List[LatestQuizData]

class AllUsersLatestDates(BaseModel):
    results: List[LatestUsersResults]


class UserQuizDetails(BaseModel):
    quiz_id: int
    details: List[QuizDetails]


class UserQuizData(BaseModel):
    user_id: int
    quiz_data: List[UserQuizDetails]


class AllMembersAvgResults(BaseModel):
    users: List[UserQuizData]


class MyLatestQuizes(BaseModel):
    results: List[LatestQuizData]
