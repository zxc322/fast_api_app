from typing import Optional
import math
from sqlalchemy import select, func
from databases import Database

from schemas import analitycs as schema_a


from datetime import datetime
from db.models import quiz as DBQuiz, question as DBQuestion, company_members as DBCompany_members, quiz_result as DBQuiz_result, avarage_mark
from utils.exceptions import MyExceptions
from repositories.services.analitycs_format import complete_results


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


    async def avg_marks_by_quiz_id(self, quiz_id: int, company_id: int):
        members_ids = await self.db.fetch_all(select(self.db_company_members.c.member_id).select_from(
            self.db_company_members).where(self.db_company_members.c.company_id==company_id)
        )

        if not members_ids:
             raise await self.exc().data_was_not_found()

        members = [member.member_id for member in members_ids]
        query = select(self.db_quiz_result.c.user_id, 
            self.db_quiz_result.c.mark, 
            self.db_quiz_result.c.created_at.label('date')).select_from(
            self.db_quiz_result).where(
                self.db_quiz_result.c.quiz_id==quiz_id,
                self.db_quiz_result.c.user_id.in_(members))

        result = await self.db.fetch_all(query=query)

        print([dict(x) for x in result])
        a = 0
        response = list()
        for i in result:
            for j in response:
                print(f'J, {len(response)}\n', j)
                if j.get('user_id') == i.user_id:
                    j['results'].append({'mark': i.mark, 'date': i.date})
                    print('\nAppend+break')
                    break
            a+=1
            print('aAAAA\n',a)
            response.append({'user_id': i.user_id, 'results':[{'mark': i.mark, 'date': i.date}]})
        print('RESPONSE', response)
        # return schema_a.AllUsersMarksByQuizId(quiz_id=quiz_id, )
        



    async def single_member_results(self, user_id: int, company_id: int) -> schema_a.ChosenUserAllQuizes:
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


            
    async def members_last_results(self, company_id: int):

        members_ids = await self.db.fetch_all(select(self.db_company_members.c.member_id).select_from(
            self.db_company_members).where(self.db_company_members.c.company_id==company_id)
        )

    

    