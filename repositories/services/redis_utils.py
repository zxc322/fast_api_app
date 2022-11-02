from my_redis.config import init_redis_pool

async def save_to_redis(user_id: int, income_quiz):
    """ Saves in format {'user_id': {'question_id': 1, 'answer': yes}. Expires in 48 hours after LAST users quiz"""
    
    my_redis = await init_redis_pool()
    for question in income_quiz.questions:        
        await my_redis.hset(user_id, question.question_id, question.chosen_option.option_name)
        await my_redis.expire(user_id, 60*60*48)