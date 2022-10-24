from typing import Optional
import math
from db.connection import database
from datetime import datetime

from db.models import company_members as DBCompany_members, users as DBUser, companies as DBCompany
from schemas.company import CreateCompany, PublicCompany, ResponseCompanyId, UpdateCompany, Company, Companies
from schemas.companies_members import Invite, ResponseMessage, MyInvites, CompanyMemberModel, UsersListInCompany
from repositories.service import paginate_data
from utils.exceptions import CustomError
from repositories.user import UserCRUD
from sqlalchemy import text
from repositories.sql_queries import GenerateSQL 

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
                is_company_admin=False,
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
        invites_instance = GenerateSQL(user_id=user_id, offset=skip, limit=limit)
        invites = await invites_instance.my_invites()
        my_invites = await database.fetch_all(text(invites))
        count_query = await invites_instance.invites_counter()
        count = await database.fetch_one(text(count_query))
        count = count.total_invites
        total_pages = math.ceil(count/limit)
        pagination = await paginate_data(page, count, total_pages, end, limit, url='company_members/my_invites')
        return MyInvites(invites=my_invites, pagination=pagination)


    async def accept_invite(self, id: int, member) -> ResponseMessage:
        if member.active_member:
            return ResponseMessage(message='You are an avtive member of this company already')
        now = datetime.utcnow()
        accept_fields = {'invited': None, 'active_member': now, 'updated_at': now}
        await database.execute(
            self.db_company_members.update().values(accept_fields).where(self.db_company_members.c.id==id)
        )
        return ResponseMessage(message='Invite accepted!')

    
    async def decline_invite(self, id: int, member) -> ResponseMessage:
        if member.active_member:
            return ResponseMessage(message='You are an avtive member of this company already')
        now = datetime.utcnow()
        await database.execute(
            self.db_company_members.delete().where(self.db_company_members.c.id==id)
        )
        return ResponseMessage(message='Invite declined!')


    async def ignore_invite(self, id: int, member) -> ResponseMessage:
        if member.active_member:
            return ResponseMessage(message='You are an avtive member of this company already')
        now = datetime.utcnow()
        accept_fields = {'invited': None, 'ignored_by_owner': True, 'updated_at': now}
        await database.execute(
            self.db_company_members.update().values(accept_fields).where(self.db_company_members.c.id==id)
        )
        return ResponseMessage(message='Invite ignored!')

    
    async def users_in_company(self, user_id: int, company_id: int) -> Optional[UsersListInCompany]:       
        company = await database.fetch_one(DBCompany.select().where(DBCompany.c.id==company_id))
        if not company.visible:
            if not company.owner_id == user_id:
                user = await database.execute(self.DBUser.select().where(DBUser.c.id==user_id))
                if not user.is_admin: 
                    member = await database.execute(self.db_company_members.select().where(
                        self.db_company_members.c.member_id==user_id))
                    if not member.is_company_admin:
                        return ResponseMessage(message="Company is private!")
        query = await GenerateSQL(company_id=company_id).users_from_company()            
        users = await database.fetch_all(text(query))
        return UsersListInCompany(users=users)

    
    async def provide_admin_status(self, company_id: int, user_id: int) -> ResponseMessage:

        member = await database.fetch_one(self.db_company_members.select().where(
            self.db_company_members.c.member_id==user_id,
            self.db_company_members.c.company_id==company_id))

        if not member or not member.active_member:
            return ResponseMessage(message='This user is not active member yet.')
        if member.is_company_admin:
            return ResponseMessage(message='This user is admin already.')
        updated_data={'is_company_admin': True, 'updated_at': datetime.utcnow()}
        await database.execute(self.db_company_members.update().values(updated_data).where(
            self.db_company_members.c.company_id==company_id,
            self.db_company_members.c.member_id==user_id))        
        return ResponseMessage(message='Admin status provided successfully.')


    async def remove_admin_status(self, company_id: int, user_id: int) -> ResponseMessage:

        member = await database.fetch_one(self.db_company_members.select().where(
            self.db_company_members.c.member_id==user_id,
            self.db_company_members.c.company_id==company_id))

        if not member or not member.active_member:
            return ResponseMessage(message='This user is not active member yet.')
        if not member.is_company_admin:
            return ResponseMessage(message='This user is not admin yet.')
        updated_data={'is_company_admin': False, 'updated_at': datetime.utcnow()}
        await database.execute(self.db_company_members.update().values(updated_data).where(
            self.db_company_members.c.company_id==company_id,
            self.db_company_members.c.member_id==user_id))        
        return ResponseMessage(message='Admin status removed successfully.')


    async def request_member_status(self, company_id: int, user_id: int) -> ResponseMessage:

        member = await database.fetch_one(self.db_company_members.select().where(
            self.db_company_members.c.member_id==user_id,
            self.db_company_members.c.company_id==company_id))

        if member:
            return ResponseMessage(message='You may not request member status in this company.')
        # chek if company exists    
        if not await database.execute(DBCompany.select().where(DBCompany.c.id==company_id)):
            return ResponseMessage(message='Company was not found.')
        now = datetime.utcnow()
        updated_data={'requested': now, 'updated_at': now, 'created_at': now, 'company_id': company_id, 'member_id': user_id}
        if await database.execute(self.db_company_members.insert().values(updated_data)):
            return ResponseMessage(message='Request was sent successfully.')

    
    async def accept_member_status(self, member: CompanyMemberModel) -> ResponseMessage:
        if not member.requested:
            return ResponseMessage(message='This user did not made a request for member status.')
        now = datetime.utcnow()
        updated_data={'requested': None, 'updated_at': now, 'created_at': now, 'active_member': now}
        await database.execute(self.db_company_members.update().values(updated_data).where(
            self.db_company_members.c.id==member.id
        ))
        return ResponseMessage(message='Request have been accepted.')


    