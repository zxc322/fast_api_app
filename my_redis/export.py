from my_redis.config import init_redis_pool
import csv
import json

from utils.exceptions import MyExceptions

class Export:
	def __init__(self):
		self.redis = init_redis_pool
		self.fields = ['total_questions', 'right_answers', 'quiz_mark','quiz_id', 'user_id', 'id', 'question', 'answer', 'is_right']


	async def get_all_my_info_from_redis(self, user_id):
		redis = await self.redis()
		data = await redis.hgetall(user_id)
		if not data:
			raise await MyExceptions().data_was_not_found()
		return data


	async def get_members_results(self, member_id: int, companies_quizes_ids: list = []):
		redis = await self.redis()
		result = list()
		for quiz_id in companies_quizes_ids:
			data = await redis.hget(member_id, quiz_id)
			if data:
				data = json.loads(data)
				new_data = await self.compile_dict_for_csv(data=data, quiz_id=quiz_id, user_id=member_id)
				result.append(new_data)
		return result


	async def compile_dict_for_csv(self, data: dict, quiz_id: int, user_id: int):
		general = data[-1]
		new_g = dict(general[0])
		new_g.update(general[1])
		new_g.update(general[2])
		new_g.update({'quiz_id': int(quiz_id), 'user_id': user_id})
		data[-1] = new_g
		return data


	
	async def create_my_results_csv(self, user_id):
		data = await self.get_all_my_info_from_redis(user_id=user_id)
		data1 = ({k: v} for k, v in data.items())

		
		filename = 'export_data/my_result.csv'

		with open(filename, 'w') as f:		
			writer = csv.DictWriter(f, fieldnames=self.fields)
			writer.writeheader()

		for i in data1:
			for k, v in i.items():
				new_data = await self.compile_dict_for_csv(data=json.loads(v), quiz_id=int(k), user_id=user_id)
				with open(filename, 'a') as f:
					writer = csv.DictWriter(f, fieldnames=self.fields)
					writer.writerows([new_data[-1]])
					writer.writerows(new_data[:-1])


	async def create_company_member_csv(self, companies_quizes_ids: list, member_id: int, create_file=True, filename=None):
		results = await self.get_members_results(member_id=member_id, companies_quizes_ids=companies_quizes_ids)

		if not filename:
			filename = 'export_data/members_result.csv'

		if create_file:
			with open(filename, 'w') as f:		
				writer = csv.DictWriter(f, fieldnames=self.fields)
				writer.writeheader()

		for data in results:
			with open(filename, 'a') as f:
				writer = csv.DictWriter(f, fieldnames=self.fields)
				writer.writerows([data[-1]])
				writer.writerows(data[:-1])

	
	async def create_all_members_csv(self, filename: str, companies_quizes_ids: list = [], members_ids: list = []):

		with open(filename, 'w') as f:		
				writer = csv.DictWriter(f, fieldnames=self.fields)
				writer.writeheader()

		for member in members_ids:
			await self.create_company_member_csv(
				companies_quizes_ids=companies_quizes_ids, 
				member_id=member, 
				create_file=False, 
				filename=filename)


	


			
