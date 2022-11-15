from typing import Optional
import math
from datetime import datetime
from sqlalchemy import select, func

from schemas import user as schems_u 
from security.auth import get_password_hash
from repositories.services.pagination import paginate_data
from utils.exceptions import CustomError
from repositories.services.generic_database import GenericDatabase



class UserCRUD(GenericDatabase):

    async def get_by_email(self, email: str) -> Optional[schems_u.IsUserAdmin]:
        user = await self.db.fetch_one(select(
            self.users_table.c.id,
            self.users_table.c.is_admin,
            self.users_table.c.password).where(
                self.users_table.c.email == email, self.users_table.c.deleted_at == None))
        return schems_u.IsUserAdmin(email=email, **user) if user else None

    
    async def create(self, user_in: schems_u.UserCreate) -> schems_u.UserRsposneId:
        now = datetime.utcnow()
        values = dict(
            username=user_in.username,
            email=user_in.email,
            password=get_password_hash(user_in.password2),
            about_me=user_in.about_me,
            is_active=False,
            is_admin=False,
            created_at=now,
            updated_at=now
        )

        user = await super().insert_values(table=self.users_table, values=values)      

        return schems_u.UserRsposneId(id=user)

    
    async def get_by_id(self, id: int) -> schems_u.User:
        if id == 0:
            raise await self.exc().id_is_0() 
        user = await self.db.fetch_one(self.users_table.select().where(
            self.users_table.c.id == id, self.users_table.c.deleted_at == None))
        if not user:
            raise CustomError(id=id)
        return schems_u.User(**user)


    async def update(self, id: int, user_in: schems_u.UpdateUser, updated_by: int) -> schems_u.UserRsposneId:
        now = datetime.utcnow()     
        updated_data = user_in.dict(skip_defaults=True)
        updated_data.update(updated_at= now, updated_by=updated_by)
        if updated_data.get('password'):
            updated_data['password'] = get_password_hash(updated_data['password'])
        await self.db.execute(self.users_table.update().values(updated_data).where(
            self.users_table.c.id==id))
        return schems_u.UserRsposneId(id=id)

    async def remove(self, id: int) -> schems_u.UserRsposneId:
        user = await self.get_by_id(id=id)
        now = datetime.utcnow()
        deleted_data = {'deleted_at':now, 'email': '[REMOVED] ' + user.email, 'updated_at': now}
        await self.db.execute(self.users_table.update().values(deleted_data).where(self.users_table.c.id==id))
        return schems_u.UserRsposneId(id=id)

    
    async def get_users(self, page: int = 1, limit: int = 10) -> schems_u.Users:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        users_on_page = self.users_table.select().where(self.users_table.c.deleted_at == None).offset(skip).limit(limit)
        total_users =  await self.db.fetch_one(select(func.count().label('nums')).select_from(
            self.users_table).where(self.users_table.c.deleted_at == None))

        queryset = await self.db.fetch_all(users_on_page)
        total_pages = math.ceil((total_users.nums)/limit)

        users = (result for result in queryset)
        pagination = await paginate_data(page, total_users.nums, total_pages, end, limit, url='users')
        return schems_u.Users(users=users, pagination=pagination)

    
    async def create_auth0_user(self, email: str) -> schems_u.UserRsposneId:
        now = datetime.utcnow()
        values = {
            'username': 'auth0User ' + email,
            'email': email,
            'password': get_password_hash(str(now)),
            'about_me': None,
            'is_active': False,
            'is_admin': False,
            'created_at': now,
            'updated_at': now
        }
        user = await super().insert_values(table=self.users_table, values=values)
        return schems_u.UserRsposneId(id=user)


        
