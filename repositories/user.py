from typing import Optional
import math
from datetime import datetime
from databases import Database
from sqlalchemy import select, func

from db.models import users as DBUser
from schemas import user as schems_u 
from security.auth import get_password_hash
from repositories.services.pagination import paginate_data
from utils.exceptions import CustomError, MyExceptions



class UserCRUD:

    def __init__(self, db: Database):
        self.db = db
        self.db_user = DBUser
        self.exc = MyExceptions

    async def get_by_email(self, email: str) -> Optional[schems_u.IsUserAdmin]:
        user = await self.db.fetch_one(select(
            self.db_user.c.id,
            self.db_user.c.is_admin,
            self.db_user.c.password).where(
                self.db_user.c.email == email, self.db_user.c.deleted_at == None))
        return schems_u.IsUserAdmin(email=email, **user) if user else None
    
    async def get_by_id(self, id: int) -> schems_u.User:
        if id == 0:
            raise await self.exc().id_is_0() 
        user = await self.db.fetch_one(self.db_user.select().where(self.db_user.c.id == id, self.db_user.c.deleted_at == None))
        if not user:
            raise CustomError(id=id)
        return schems_u.User(**user)

    async def create(self, user_in: schems_u.UserCreate) -> schems_u.UserRsposneId:
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
        return schems_u.UserRsposneId(id=await self.db.execute(user))


    async def update(self, id: int, user_in: schems_u.UpdateUser, updated_by: int) -> schems_u.UserRsposneId:
        now = datetime.utcnow()     
        updated_data = user_in.dict(skip_defaults=True)
        updated_data.update(updated_at= now, updated_by=updated_by)
        if updated_data.get('password'):
            updated_data['password'] = get_password_hash(updated_data['password'])
        await self.db.execute(self.db_user.update().values(updated_data).where(self.db_user.c.id==id))
        return schems_u.UserRsposneId(id=id)

    async def remove(self, id: int) -> schems_u.UserRsposneId:
        user = await self.get_by_id(id=id)
        now = datetime.utcnow()
        deleted_data = {'deleted_at':now, 'email': '[REMOVED] ' + user.email, 'updated_at': now}
        await self.db.execute(self.db_user.update().values(deleted_data).where(self.db_user.c.id==id))
        return schems_u.UserRsposneId(id=id)


    async def get_users(self, page: int = 1, limit: int = 10) -> schems_u.Users:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        users_on_page = self.db_user.select().where(self.db_user.c.deleted_at == None).offset(skip).limit(limit)
        total_users =  await self.db.fetch_one(select(func.count().label('nums')).select_from(
            self.db_user).where(self.db_user.c.deleted_at == None))

        queryset = await self.db.fetch_all(users_on_page)
        total_pages = math.ceil((total_users.nums)/limit)

        users = (result for result in queryset)
        pagination = await paginate_data(page, total_users.nums, total_pages, end, limit, url='users')
        return schems_u.Users(users=users, pagination=pagination)


    async def create_auth0_user(self, email: str) -> schems_u.UserRsposneId:
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
        return schems_u.UserRsposneId(id=await self.db.execute(user))
        
