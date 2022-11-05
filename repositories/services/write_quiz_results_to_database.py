from datetime import datetime

class InsertQuizResultToDatabase:

    def __init__(self, db, average_table, quiz_results_table, data):
        self.db = db
        self.average_table = average_table
        self.data = data
        self.quiz_results_table = quiz_results_table

    async def save_quiz_results(self):
        await self.db.execute(self.quiz_results_table.insert().values(self.data))    


    async def rewrite_avg_mark(self):
        data = self.data.copy()
        del data['quiz_id']
        
        user_data = await self.db.fetch_one(self.average_table.select().where(
            self.average_table.c.user_id==data.get('user_id')))
        if not user_data:
            new_data = data.copy()      
            new_data['quizzes_passed'] = 1
            new_data['avarage_mark'] = new_data.pop('mark')
            return await self.db.execute(self.average_table.insert().values(new_data))
        updated_data = dict()
        updated_data['quizzes_passed'] = user_data.quizzes_passed + 1
        updated_data['total_questions'] = user_data.total_questions + data.get('total_questions')
        updated_data['right_answers'] = user_data.right_answers + data.get('right_answers')
        updated_data['avarage_mark'] =  (updated_data.get('right_answers') / updated_data.get('total_questions')) *10
        updated_data['updated_at'] = datetime.utcnow()
        return await self.db.execute(self.average_table.update().values(updated_data).where(
            self.average_table.c.user_id==data.get('user_id')))
