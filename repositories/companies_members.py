from typing import Optional
import math
from db.connection import database
from datetime import datetime

from db.models import company_members as DBCompany_members, user as DBUser, company as DBCompany
from schemas.company import CreateCompany, PublicCompany, ResponseCompanyId, UpdateCompany, Company, Companies
from schemas.companies_members import Invite, ResponseMessage, MyInvites, CompanyMemberModel, UsersListInCompany
from repositories.service import paginate_data
from utils.exceptions import CustomError
from repositories.user import UserCRUD


class CompanyMemberCRUD:

    def __init__(self, db_company_members: DBCompany_members = None):
        self.db_company_members = db_company_members

    async def get_by_id(self, id: int) -> CompanyMemberModel:
        response = await database.fetch_one(self.db_company_members.select().where(self.db_company_members.c.id==id))
        if not response:
            raise CustomError(wrong_member_id=True)
        return CompanyMemberModel(**response)   

    async def invite_member(self, invite: Invite) -> ResponseMessage:
        relation = await database.fetch_one(self.db_company_members.select().where(
            self.db_company_members.c.company_id == invite.company_id,
            self.db_company_members.c.member_id == invite.user_id))
        now = datetime.utcnow()

        if not relation:
            # chek if user exists
            await UserCRUD(db_user=DBUser).get_by_id(id=invite.user_id)

            invitation = self.db_company_members.insert().values(
                company_id=invite.company_id,
                member_id=invite.user_id,
                invited=now,
                created_at=now,
                updated_at=now,
            )
            await database.execute(invitation)
            return ResponseMessage(message='Invitation have been sent.')
        elif relation.invited:
            return ResponseMessage(message='This user invitated already.')
        elif relation.ignored_by_user:
            return ResponseMessage(message='This user blocked invited from your company :(')

    async def my_invites(self, user_id: int, page: int = 1, limit: int = 10) -> MyInvites:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit
        query = self.db_company_members.select().where(
            self.db_company_members.c.member_id == user_id, 
            self.db_company_members.c.invited != None)
    
        my_invites = await database.fetch_all(query.offset(skip).limit(limit))
        count = len(await database.fetch_all(query))
        result = []
        for invite in my_invites:
            res = dict(invite)
            res['company'] = await database.fetch_one(DBCompany.select().where(DBCompany.c.id==invite.company_id))
            result.append(res)

        total_pages = math.ceil(count/limit)
        pagination = await paginate_data(page, count, total_pages, end, limit, url='company_members/my_invites')
        return MyInvites(invites=result, pagination=pagination)


    async def accept_invite(self, id: int) -> ResponseMessage:
        member = await self.get_by_id(id=id)
        if member.active_member:
            return ResponseMessage(message='You are an avtive member of this company already')
        now = datetime.utcnow()
        accept_fields = {'invited': None, 'active_member': now, 'updated_at': now}
        await database.execute(
            self.db_company_members.update().values(accept_fields).where(self.db_company_members.c.id==id)
        )
        return ResponseMessage(message='Invite accepted!')

    
    async def decline_invite(self, id: int) -> ResponseMessage:
        member = await self.get_by_id(id=id)
        if member.active_member:
            return ResponseMessage(message='You are an avtive member of this company already')
        now = datetime.utcnow()
        await database.execute(
            self.db_company_members.delete().where(self.db_company_members.c.id==id)
        )
        return ResponseMessage(message='Invite declined!')


    async def ignore_invite(self, id: int) -> ResponseMessage:
        member = await self.get_by_id(id=id)
        if member.active_member:
            return ResponseMessage(message='You are an avtive member of this company already')
        now = datetime.utcnow()
        accept_fields = {'invited': None, 'ignored_by_owner': True, 'updated_at': now}
        await database.execute(
            self.db_company_members.update().values(accept_fields).where(self.db_company_members.c.id==id)
        )
        return ResponseMessage(message='Invite ignored!')

    
    async def users_in_company(self, user_id: int, company_id: int, page: int = 1, limit: int = 10) -> Optional[UsersListInCompany]:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit
        
        company = await database.fetch_one(DBCompany.select().where(DBCompany.c.id==company_id))
        if company.visible or company.owner_id == user_id:
            query = self.db_company_members.select().where(
                self.db_company_members.c.company_id == company_id, 
                self.db_company_members.c.active_member != None)
            users = await database.fetch_all(query.offset(skip).limit(limit))
            count = len(await database.fetch_all(query))
            result = []
            for user in users:
                res = dict()
                res['id'] = user.id
                res['active_member_from'] = user.active_member
                res['user'] = dict(await database.fetch_one(DBUser.select().where(DBUser.c.id==user.id)))
                result.append(res)
            
            total_pages = math.ceil(count/limit)
            pagination = await paginate_data(page, count, total_pages, end, limit, url=f'company_members/{company_id}/users')
            return UsersListInCompany(users=result, pagination=pagination)
        else:
            return ResponseMessage(message="Company is private!") 