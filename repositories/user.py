from typing import Optional
import math
from db.connection import database
from datetime import datetime

from db.models import user as DBUser
from schemas.user import UserCreate, User, Users, UserRsposneId, UpdateUser
from security.auth import get_password_hash
from repositories.service import paginate_data
from utils.exceptions import CustomError


class UserCRUD:

    def __init__(self, db_user: DBUser = None):
        self.db_user = db_user
    
    async def get_by_email(self, email) -> Optional[User]:
        user = await database.fetch_one(self.db_user.select().where(self.db_user.c.email == email, self.db_user.c.deleted_at == None))
        return User(**user) if user else None
    
    async def get_by_id(self, id: int) -> User:
        user = await database.fetch_one(self.db_user.select().where(self.db_user.c.id == id, self.db_user.c.deleted_at == None))
        if not user:
            raise CustomError(id=id)
        return User(**user)

    async def create(self, user_in: UserCreate) -> UserRsposneId:
        now = datetime.utcnow()
        user = self.db_user.insert().values(
            username=user_in.username,
            email=user_in.email,
            password=get_password_hash(user_in.password2),
            about_me=user_in.about_me,
            is_active=False,
            is_admin=False,
            created_at=now,
            updated_at=now
        )      
        return UserRsposneId(id=await database.execute(user))


    async def update(self, id: int, user_in: UpdateUser) -> UserRsposneId:
        now = datetime.utcnow()     
        updated_data = user_in.dict(skip_defaults=True)
        updated_data['updated_at'] = now
        if updated_data.get('password'):
            updated_data['password'] = get_password_hash(updated_data['password'])
        u = self.db_user.update().values(updated_data).where(self.db_user.c.id==id)
        await database.execute(u)
        return UserRsposneId(id=id)

    async def remove(self, id: int) -> UserRsposneId:
        user = await self.get_by_id(id=id)
        now = datetime.utcnow()
        deleted_data = {'deleted_at':now, 'email': '[REMOVED] ' + user.email, 'updated_at': now}
        u = self.db_user.update().values(deleted_data).where(self.db_user.c.id==id)
        await database.execute(u)
        return UserRsposneId(id=id)


    async def get_users(self, page: int = 1, limit: int = 10) -> Users:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        users_on_page = self.db_user.select().where(self.db_user.c.deleted_at == None).offset(skip).limit(limit)
        total_users =  self.db_user.select().where(self.db_user.c.deleted_at == None)
        count = len(await database.fetch_all(total_users))
        
        queryset = await database.fetch_all(users_on_page)
        total_pages = math.ceil(count/limit)

        users = [dict(result) for result in queryset]
        pagination = await paginate_data(page, count, total_pages, end, limit, url='users')
        return Users(users=users, pagination=pagination)


    async def create_auth0_user(self, email: str) -> UserRsposneId:
        now = datetime.utcnow()
        user_dict = {
            'username': 'auth0User ' + email,
            'email': email,
            'password': get_password_hash(str(now)),
            'about_me': None,
            'is_active': False,
            'is_admin': False,
            'created_at': now,
            'updated_at': now
        }
        user = self.db_user.insert().values(user_dict)     
        new_user_id = {'id': await database.execute(user)}
        return UserRsposneId(**new_user_id)
        
