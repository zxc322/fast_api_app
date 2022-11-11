from typing import Optional
import math
from datetime import datetime
from sqlalchemy import select, func

from schemas import companies_members as schema_cm
from repositories.services.pagination import paginate_data
from utils.exceptions import CustomError
from repositories.user import UserCRUD
from repositories.services.generic_database import GenericDatabase


class CompanyMemberCRUD(GenericDatabase):


    async def get_by_id(self, id: int) -> schema_cm.CompanyMemberModel:
        response = await self.db.fetch_one(self.company_members_table.select().where(
            self.company_members_table.c.id==id))
        if not response:
            raise CustomError(wrong_member_id=True)
        return schema_cm.CompanyMemberModel(**response)  


    async def is_company_admin(self, user_id: int, company_id: int) -> bool:
        member = await self.db.fetch_one(self.company_members_table.select().where(
            self.company_members_table.c.member_id==user_id,
            self.company_members_table.c.company_id==company_id,
            ))
        if not member or not member.is_company_admin:
            return False
        return True

    async def invite_member(self, invite: schema_cm.Invite) -> schema_cm.ResponseMessage:
        relation = await self.db.fetch_one(self.company_members_table.select().where(
            self.company_members_table.c.company_id == invite.company_id,
            self.company_members_table.c.member_id == invite.user_id))
        now = datetime.utcnow()

        if not relation:
            # chek if user exists
            await UserCRUD(db=self.db).get_by_id(id=invite.user_id)

            values = dict(
                company_id=invite.company_id,
                member_id=invite.user_id,
                is_company_admin=False,
                invited=now,
                created_at=now,
                updated_at=now
            )
            await super().insert_values(table=self.company_members_table, values=values)
            return schema_cm.ResponseMessage(message='Invitation have been sent.')

        elif relation.invited:
            raise await self.exception().invited_already()
        elif relation.ignored_by_user:
            raise await self.exception().blocked()


    async def my_invites(self, user_id: int, page: int = 1, limit: int = 10) -> schema_cm.MyInvites:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        companies_query = select(self.company_table.c.id.label('company_id'),
            self.company_table.c.name.label('company_name'),
            self.company_table.c.description.label('company_description'),
            self.company_table.c.owner_id.label('owner_id')
            ).subquery()

        query = select(self.company_members_table.c.id.label('member_id'), 
            self.company_members_table.c.invited,
            companies_query).select_from(
                self.company_members_table.join(companies_query)).where(
                    self.company_members_table.c.member_id==user_id,
                    self.company_members_table.c.invited!=None
                ).limit(limit).offset(skip)
        
        count_query = select([func.count().label('total_invites')]).select_from(
            self.company_members_table).where(
                self.company_members_table.c.member_id==user_id,
                        self.company_members_table.c.invited!=None
            )

        my_invites = await self.db.fetch_all(query=query)
        count = await self.db.fetch_one(count_query)
        count = count.total_invites
        total_pages = math.ceil(count/limit)
        pagination = await paginate_data(page, count, total_pages, end, limit, url='company_members/my_invites')
        return schema_cm.MyInvites(invites=my_invites, pagination=pagination)



    async def accept_invite(self, id: int, member) -> schema_cm.ResponseMessage:
        if member.active_member:
            raise await self.exception().active_already()
        now = datetime.utcnow()
        accept_fields = {'invited': None, 'active_member': now, 'updated_at': now}
        await self.db.execute(
            self.company_members_table.update().values(accept_fields).where(
                self.company_members_table.c.id==id)
            )
        return schema_cm.ResponseMessage(message='Invite accepted!')

    
    async def decline_invite(self, id: int, member) -> schema_cm.ResponseMessage:
        if member.active_member:
            raise await self.exception().active_already()
        await self.db.execute(
            self.company_members_table.delete().where(self.company_members_table.c.id==id)
        )
        return schema_cm.ResponseMessage(message='Invite declined!')


    async def ignore_invite(self, id: int, member) -> schema_cm.ResponseMessage:
        if member.active_member:
            raise await self.exception().active_already()
        now = datetime.utcnow()
        ignore_fields = {'invited': None, 'ignored_by_user': True, 'updated_at': now}
        await self.db.execute(
            self.company_members_table.update().values(ignore_fields).where(
                self.company_members_table.c.id==id)
            )
        return schema_cm.ResponseMessage(message='Invite ignored!')

    
    async def users_in_company(self, user_id: int, company_id: int) -> Optional[schema_cm.UsersListInCompany]:       
        company = await self.db.fetch_one(self.company_table.select().where(
            self.company_table.c.id==company_id))
        if not company.visible:
            # This block execute if company status != visible

            if not company.owner_id == user_id:
                user = await self.db.execute(self.users_table.select().where(
                    self.users_table.c.id==user_id))
                if not user.is_admin: 
                    member = await self.db.execute(self.company_members_table.select().where(
                        self.company_members_table.c.member_id==user_id))
                    if not member.is_company_admin:
                        return schema_cm.ResponseMessage(message="Company is private!")
           
        
        users_query = select(self.users_table.c.id.label('user_id'),
            self.users_table.c.username).subquery()

        query = select(self.company_members_table.c.id.label('member_id'),
            self.company_members_table.c.active_member.label('active_member_from'),
            self.company_members_table.c.company_id.label('company_id'),
            self.company_members_table.c.is_company_admin,
            users_query).select_from(
            self.company_members_table.join(users_query)).where(
                self.company_members_table.c.active_member!=None,
                self.company_members_table.c.company_id==company_id
            )
     
        users = await self.db.fetch_all(query=query)
        return schema_cm.UsersListInCompany(users=users)

    
    async def provide_admin_status(self, company_id: int, user_id: int) -> schema_cm.ResponseMessage:

        member = await self.db.fetch_one(self.company_members_table.select().where(
            self.company_members_table.c.member_id==user_id,
            self.company_members_table.c.company_id==company_id))

        if not member or not member.active_member:
            raise await self.exception().not_active_yet()
        if member.is_company_admin:
            raise await self.exception().is_admin_already()
        updated_data={'is_company_admin': True, 'updated_at': datetime.utcnow()}
        await self.db.execute(self.company_members_table.update().values(updated_data).where(
            self.company_members_table.c.company_id==company_id,
            self.company_members_table.c.member_id==user_id))        
        return schema_cm.ResponseMessage(message='Admin status provided successfully.')


    async def remove_admin_status(self, company_id: int, user_id: int) -> schema_cm.ResponseMessage:

        member = await self.db.fetch_one(self.company_members_table.select().where(
            self.company_members_table.c.member_id==user_id,
            self.company_members_table.c.company_id==company_id))

        if not member or not member.active_member:
            raise await self.exception().not_active_yet()
        if not member.is_company_admin:
            raise await self.exception().is_not_admin_yet()
        updated_data={'is_company_admin': False, 'updated_at': datetime.utcnow()}
        await self.db.execute(self.company_members_table.update().values(updated_data).where(
            self.company_members_table.c.company_id==company_id,
            self.company_members_table.c.member_id==user_id))        
        return schema_cm.ResponseMessage(message='Admin status removed successfully.')


    async def request_member_status(self, company_id: int, user_id: int) -> schema_cm.ResponseMessage:

        member = await self.db.fetch_one(self.company_members_table.select().where(
            self.company_members_table.c.member_id==user_id,
            self.company_members_table.c.company_id==company_id))

        if member:
            raise await self.exception().you_just_may_not()

        # chek if company exists    
        company = await self.db.fetch_one(select(self.company_table.c.id).select_from(
            self.company_table).where(self.company_table.c.id==company_id))
        if not company:
            raise await self.exception().data_was_not_found()
        now = datetime.utcnow()
        updated_data={'requested': now, 'updated_at': now, 'created_at': now, 'company_id': company_id, 'member_id': user_id, 'is_company_admin': False}
        if await self.db.execute(self.company_members_table.insert().values(updated_data)):
            return schema_cm.ResponseMessage(message='Request was sent successfully.')

    
    async def accept_member_status(self, member: schema_cm.CompanyMemberModel) -> schema_cm.ResponseMessage:
        if not member.requested:
            raise await self.exception().not_requested()
        now = datetime.utcnow()
        updated_data={'requested': None, 'updated_at': now, 'created_at': now, 'active_member': now}
        await self.db.execute(self.company_members_table.update().values(updated_data).where(
            self.company_members_table.c.id==member.id
        ))
        return schema_cm.ResponseMessage(message='Request have been accepted.')


    async def check_is_user_active_company_member(self, user_id: int, company_id: int) -> Optional[bool]:
        member = await self.db.fetch_one(select(self.company_members_table.c.id).select_from(
            self.company_members_table).where(
                self.company_members_table.c.member_id==user_id,
                self.company_members_table.c.company_id==company_id,
                self.company_members_table.c.active_member!=None
                ))
            

        if member:
            return True
 

    async def membres_of_chosen_company(self, company_id: int) -> Optional[list]:
        """ Returns list with ids users of chosen company (we need it for redis queries) """

        members = await self.db.fetch_all(select(self.company_members_table.c.member_id).where(
            self.company_members_table.c.company_id==company_id,
            self.company_members_table.c.active_member!=None
            ))

        if members:
            return [dict(i).get('member_id') for i in members]
    

    async def companies_where_user_is_active_member(self, user_id: int) -> schema_cm.ListUsersCompanies:
        """ List od companies where authorized user is active member """

        query = await self.company_members_join_company()
        query = query.where(
                self.company_table.c.deleted_at==None,
                self.company_members_table.c.member_id==user_id, 
                self.company_members_table.c.active_member!=None)

        return schema_cm.ListUsersCompanies(companies=await self.db.fetch_all(query=query))
    
    async def companies_where_user_is_admin(self, user_id: int):
        """ List od companies where authorized user is active member """

        query = await self.company_members_join_company()
        query = query.where(
                self.company_table.c.deleted_at==None,
                self.company_members_table.c.member_id==user_id, 
                self.company_members_table.c.is_company_admin==True)

        return schema_cm.ListUsersCompanies(companies=await self.db.fetch_all(query=query))


    async def leave_company(self, company_id: int, user_id: int, message: str) -> schema_cm.ResponseMessage:
        
        member = await self.db.fetch_one(select(self.company_members_table.c.active_member).select_from(
                self.company_members_table).where(
                    self.company_members_table.c.member_id==user_id,
                    self.company_members_table.c.company_id==company_id
                )
            )

        if not member:
            raise await self.exception().not_active_yet()
        await self.db.execute(self.company_members_table.delete().where(
            self.company_members_table.c.company_id==company_id,
            self.company_members_table.c.member_id==user_id))        
        return schema_cm.ResponseMessage(message=message)


    async def requests_for_membership(self, company_id: int) -> schema_cm.RequestsMembership:
        """ Endpoints for companies admins ( returns users list, whos made a request for participating chosen company """

        query = select(
            self.company_members_table.c.id.label('request_id'),
            self.company_members_table.c.member_id.label('user_id'),
            self.company_members_table.c.requested.label('from_date'),          
            ).select_from(self.company_members_table).where(
                self.company_members_table.c.company_id==company_id,
                self.company_members_table.c.requested!=None
            )
        resposne = await self.db.fetch_all(query=query)
        
        return schema_cm.RequestsMembership(requests=resposne)
    
    