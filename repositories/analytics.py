from typing import Optional
import math
from sqlalchemy import select, func, distinct, desc
from databases import Database

from schemas import analitycs as schema_a


from datetime import datetime
from db.models import quiz as DBQuiz, question as DBQuestion, company_members as DBCompany_members, quiz_result as DBQuiz_result, avarage_mark
from utils.exceptions import MyExceptions
from repositories.services.analitycs_format import complete_results, complete_pretty_dict


class AnalitycsCRUD:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.db_quiz = DBQuiz
        self.db_question = DBQuestion
        self.db_company_members = DBCompany_members
        self.db_quiz_result = DBQuiz_result
        self.db_avarage_mark = avarage_mark
        self.exc = MyExceptions


    async def my_all_quizes_avg(self, user_id) -> schema_a.MyAvgMark:
        """ An avarage mark + statistic about chosen user """

        mark = await self.db.fetch_one(select(
            self.db_avarage_mark.c.quizzes_passed,
            self.db_avarage_mark.c.total_questions,
            self.db_avarage_mark.c.right_answers,
            self.db_avarage_mark.c.avarage_mark).select_from(
            self.db_avarage_mark).where(self.db_avarage_mark.c.user_id==user_id)
        )
        if not mark:
            raise await self.exc().data_was_not_found()
        return schema_a.MyAvgMark(**dict(mark))


    async def my_results_of_chosen_quiz(self, user_id: int, quiz_id: int):
        """ Results authorized user of chozen quiz"""

        query = select(
            self.db_quiz_result.c.total_questions,
            self.db_quiz_result.c.right_answers,
            self.db_quiz_result.c.mark,
            self.db_quiz_result.c.created_at.label('date')
                ).select_from(self.db_quiz_result).where(
                    self.db_quiz_result.c.user_id==user_id,
                    self.db_quiz_result.c.quiz_id==quiz_id
                    )
        
        results = await self.db.fetch_all(query=query)
        return schema_a.MyAvgMarkOfChosenQuizList(my_results=[dict(x) for x in results])



    async def my_quizes_latest_date(self, user_id):
        """ List of authorized user quizes latest date """

        query = select(
            self.db_quiz_result.c.quiz_id,
            self.db_quiz_result.c.created_at.label('date')
                ).select_from(self.db_quiz_result).where(
                    self.db_quiz_result.c.user_id==user_id
                    ).order_by(desc(self.db_quiz_result.c.created_at))

        results = await self.db.fetch_all(query=query)
        response = list()

        for record in results:
            if response:               
                if record.quiz_id not in [x.get('quiz_id') for x in response]:
                    response.append(dict(
                        quiz_id=record.quiz_id,
                        date=record.date
                    ))
            else:
                response.append(dict(
                            quiz_id=record.quiz_id,
                            date=record.date
                        ))

        return schema_a.MyLatestQuizes(results=response)


    async def avg_marks_by_quiz_id(self, company_id: int) -> schema_a.AllMembersAvgResults:
        """ Avarage mark all members of chosen company """

        members_ids = await self.db.fetch_all(select(self.db_company_members.c.member_id).select_from(
            self.db_company_members).where(self.db_company_members.c.company_id==company_id)
        )

        quizes_ids = await self.db.fetch_all(select(self.db_quiz.c.id).select_from(
            self.db_quiz).where(self.db_quiz.c.company_id==company_id)
        )

        if not members_ids or not quizes_ids:
             raise await self.exc().data_was_not_found()


        members = [member.member_id for member in members_ids]
        quizes = [dict(quiz).get('id') for quiz in quizes_ids]
        response = [dict(user_id=d, quiz_data=list()) for d in members]

        query = select(
            self.db_quiz_result.c.user_id,
            self.db_quiz_result.c.quiz_id, 
            self.db_quiz_result.c.total_questions,
            self.db_quiz_result.c.right_answers,
            self.db_quiz_result.c.mark,
            self.db_quiz_result.c.created_at.label('date')).select_from(
            self.db_quiz_result).where(
                self.db_quiz_result.c.user_id.in_(members),
                self.db_quiz_result.c.quiz_id.in_(quizes))

        results = await self.db.fetch_all(query=query)

        await complete_pretty_dict(results=results, response=response)

        return schema_a.AllMembersAvgResults(users=response)


    async def single_member_results(self, user_id: int, company_id: int) -> schema_a.ChosenUserAllQuizes:
        """ Results of chosen user ( All quizes of chosen company) """

        quizes_ids = await self.db.fetch_all(select(self.db_quiz.c.id).select_from(
            self.db_quiz).where(self.db_quiz.c.company_id==company_id)
        )

        quizes = [dict(quiz).get('id') for quiz in quizes_ids]
        query = select(
            self.db_quiz_result.c.quiz_id, 
            self.db_quiz_result.c.mark, 
            self.db_quiz_result.c.total_questions,
            self.db_quiz_result.c.right_answers,
            self.db_quiz_result.c.created_at.label('date')).select_from(
            self.db_quiz_result).where(
                self.db_quiz_result.c.user_id==user_id,
                self.db_quiz_result.c.quiz_id.in_(quizes))
        data = await self.db.fetch_all(query=query)       
        return await complete_results(data)


    
    async def members_list_latest_results(self, company_id: int) -> schema_a.AllUsersLatestDates:

        members_ids = await self.db.fetch_all(select(self.db_company_members.c.member_id).select_from(
            self.db_company_members).where(self.db_company_members.c.company_id==company_id)
        )

        quizes_ids = await self.db.fetch_all(select(self.db_quiz.c.id).select_from(
            self.db_quiz).where(self.db_quiz.c.company_id==company_id)
        )

        if not members_ids or not quizes_ids:
             raise await self.exc().data_was_not_found()

        members = [member.member_id for member in members_ids]
        quizes = [dict(quiz).get('id') for quiz in quizes_ids]
        response = [dict(user_id=d, quiz_data=list()) for d in members]

        query = select(
            self.db_quiz_result.c.user_id,
            self.db_quiz_result.c.quiz_id, 
            self.db_quiz_result.c.created_at
                ).select_from(
                    self.db_quiz_result).where(
                        self.db_quiz_result.c.user_id.in_(members),
                        self.db_quiz_result.c.quiz_id.in_(quizes)
                    ).order_by(desc(self.db_quiz_result.c.created_at))


        results = await self.db.fetch_all(query=query)
        
        for record in results:
            for res in response:
                if record.user_id == res.get('user_id'):
                    quizes = [x.get('quiz_id') for x in res.get('quiz_data')]
                    if record.quiz_id not in quizes:
                        res.get('quiz_data').append(dict(quiz_id=record.quiz_id, date=record.created_at))

        return schema_a.AllUsersLatestDates(results=response)
    

    