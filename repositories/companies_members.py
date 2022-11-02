from typing import Optional
import math
from databases import Database
from datetime import datetime

from db.models import company_members as DBCompany_members, users as DBUser, companies as DBCompany
from schemas.companies_members import Invite, ResponseMessage, MyInvites, CompanyMemberModel, UsersListInCompany
from repositories.services.pagination import paginate_data
from utils.exceptions import CustomError, MyExceptions
from repositories.user import UserCRUD
from sqlalchemy import select, func


class CompanyMemberCRUD:

    def __init__(self, db: Database):
        self.db = db
        self.db_company_members = DBCompany_members
        self.exception = MyExceptions

    async def get_by_id(self, id: int) -> CompanyMemberModel:
        response = await self.db.fetch_one(self.db_company_members.select().where(self.db_company_members.c.id==id))
        if not response:
            raise CustomError(wrong_member_id=True)
        return CompanyMemberModel(**response)  


    async def is_company_admin(self, user_id: int, company_id: int) -> bool:
        member = await self.db.fetch_one(self.db_company_members.select().where(
            self.db_company_members.c.member_id==user_id,
            self.db_company_members.c.company_id==company_id,
            ))
        if not member or not member.is_company_admin:
            return False
        return True

    async def invite_member(self, invite: Invite) -> ResponseMessage:
        relation = await self.db.fetch_one(self.db_company_members.select().where(
            self.db_company_members.c.company_id == invite.company_id,
            self.db_company_members.c.member_id == invite.user_id))
        now = datetime.utcnow()

        if not relation:
            # chek if user exists
            await UserCRUD().get_by_id(id=invite.user_id)

            invitation = self.db_company_members.insert().values(
                company_id=invite.company_id,
                member_id=invite.user_id,
                is_company_admin=False,
                invited=now,
                created_at=now,
                updated_at=now
            )
            await self.db.execute(invitation)
            return ResponseMessage(message='Invitation have been sent.')
        elif relation.invited:
            raise await self.exception().invited_already()
        elif relation.ignored_by_user:
            raise await self.exception().blocked()


    async def my_invites(self, user_id: int, page: int = 1, limit: int = 10) -> MyInvites:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        companies_query = select(DBCompany.c.id.label('company_id'),
            DBCompany.c.name.label('company_name'),
            DBCompany.c.description.label('company_description'),
            DBCompany.c.owner_id.label('owner_id')
            ).subquery()

        query = select(self.db_company_members.c.id.label('member_id'), 
            self.db_company_members.c.invited,
            companies_query).select_from(
                self.db_company_members.join(companies_query)).where(
                    self.db_company_members.c.member_id==user_id,
                    self.db_company_members.c.invited!=None
                ).limit(limit).offset(skip)
        
        count_query = select([func.count().label('total_invites')]).select_from(self.db_company_members).where(
            self.db_company_members.c.member_id==user_id,
                    self.db_company_members.c.invited!=None
        )

        my_invites = await self.db.fetch_all(query=query)
        count = await self.db.fetch_one(count_query)
        count = count.total_invites
        total_pages = math.ceil(count/limit)
        pagination = await paginate_data(page, count, total_pages, end, limit, url='company_members/my_invites')
        return MyInvites(invites=my_invites, pagination=pagination)



    async def accept_invite(self, id: int, member) -> ResponseMessage:
        if member.active_member:
            raise await self.exception().active_already()
        now = datetime.utcnow()
        accept_fields = {'invited': None, 'active_member': now, 'updated_at': now}
        await self.db.execute(
            self.db_company_members.update().values(accept_fields).where(self.db_company_members.c.id==id)
        )
        return ResponseMessage(message='Invite accepted!')

    
    async def decline_invite(self, id: int, member) -> ResponseMessage:
        if member.active_member:
            raise await self.exception().active_already()
        await self.db.execute(
            self.db_company_members.delete().where(self.db_company_members.c.id==id)
        )
        return ResponseMessage(message='Invite declined!')


    async def ignore_invite(self, id: int, member) -> ResponseMessage:
        if member.active_member:
            raise await self.exception().active_already()
        now = datetime.utcnow()
        accept_fields = {'invited': None, 'ignored_by_user': True, 'updated_at': now}
        await self.db.execute(
            self.db_company_members.update().values(accept_fields).where(self.db_company_members.c.id==id)
        )
        return ResponseMessage(message='Invite ignored!')

    
    async def users_in_company(self, user_id: int, company_id: int) -> Optional[UsersListInCompany]:       
        company = await self.db.fetch_one(DBCompany.select().where(DBCompany.c.id==company_id))
        if not company.visible:
            if not company.owner_id == user_id:
                user = await self.db.execute(self.DBUser.select().where(DBUser.c.id==user_id))
                if not user.is_admin: 
                    member = await self.db.execute(self.db_company_members.select().where(
                        self.db_company_members.c.member_id==user_id))
                    if not member.is_company_admin:
                        return ResponseMessage(message="Company is private!")
           
        
        users_query = select(DBUser.c.id.label('user_id'),
            DBUser.c.username).subquery()

        query = select(self.db_company_members.c.id.label('member_id'),
            self.db_company_members.c.active_member.label('active_member_from'),
            self.db_company_members.c.company_id.label('company_id'),
            self.db_company_members.c.is_company_admin,
            users_query).select_from(
            self.db_company_members.join(users_query)).where(
                self.db_company_members.c.active_member!=None,
                self.db_company_members.c.company_id==company_id
            )
     
        users = await self.db.fetch_all(query=query)
        return UsersListInCompany(users=users)

    
    async def provide_admin_status(self, company_id: int, user_id: int) -> ResponseMessage:

        member = await self.db.fetch_one(self.db_company_members.select().where(
            self.db_company_members.c.member_id==user_id,
            self.db_company_members.c.company_id==company_id))

        if not member or not member.active_member:
            raise await self.exception().not_active_yet()
        if member.is_company_admin:
            raise await self.exception().is_admin_already()
        updated_data={'is_company_admin': True, 'updated_at': datetime.utcnow()}
        await self.db.execute(self.db_company_members.update().values(updated_data).where(
            self.db_company_members.c.company_id==company_id,
            self.db_company_members.c.member_id==user_id))        
        return ResponseMessage(message='Admin status provided successfully.')


    async def remove_admin_status(self, company_id: int, user_id: int) -> ResponseMessage:

        member = await self.db.fetch_one(self.db_company_members.select().where(
            self.db_company_members.c.member_id==user_id,
            self.db_company_members.c.company_id==company_id))

        if not member or not member.active_member:
            raise await self.exception().not_active_yet()
        if not member.is_company_admin:
            raise await self.exception().is_not_admin_yet()
        updated_data={'is_company_admin': False, 'updated_at': datetime.utcnow()}
        await self.db.execute(self.db_company_members.update().values(updated_data).where(
            self.db_company_members.c.company_id==company_id,
            self.db_company_members.c.member_id==user_id))        
        return ResponseMessage(message='Admin status removed successfully.')


    async def request_member_status(self, company_id: int, user_id: int) -> ResponseMessage:

        member = await self.db.fetch_one(self.db_company_members.select().where(
            self.db_company_members.c.member_id==user_id,
            self.db_company_members.c.company_id==company_id))

        if member:
            raise await self.exception().you_just_may_not()

        # chek if company exists    
        await self.db.execute(DBCompany.select().where(DBCompany.c.id==company_id))
        now = datetime.utcnow()
        updated_data={'requested': now, 'updated_at': now, 'created_at': now, 'company_id': company_id, 'member_id': user_id, 'is_company_admin': False}
        if await self.db.execute(self.db_company_members.insert().values(updated_data)):
            return ResponseMessage(message='Request was sent successfully.')

    
    async def accept_member_status(self, member: CompanyMemberModel) -> ResponseMessage:
        if not member.requested:
            raise await self.exception().not_requested()
        now = datetime.utcnow()
        updated_data={'requested': None, 'updated_at': now, 'created_at': now, 'active_member': now}
        await self.db.execute(self.db_company_members.update().values(updated_data).where(
            self.db_company_members.c.id==member.id
        ))
        return ResponseMessage(message='Request have been accepted.')


    