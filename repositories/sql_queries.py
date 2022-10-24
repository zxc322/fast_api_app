class GenerateSQL:
    
    def __init__(self, company_id: int = None, user_id: int = None, offset: int = None, limit: int = None):
        self.company_id = company_id
        self.offset = offset
        self.limit = limit
        self.user_id = user_id

    
    async def users_from_company(self):
        query = f'SELECT company_members.id as member_id,\
            companies.id as company_id,\
            companies.name as company_name,\
            active_member as active_member_from,\
            is_company_admin,\
            users.id as user_id,\
            users.username\
            FROM company_members\
            INNER JOIN users \
            ON company_members.member_id = users.id\
            JOIN companies \
            ON company_members.company_id = companies.id\
            WHERE active_member IS NOT NULL AND company_id = {self.company_id}'
        return query

    
    async def my_invites(self):
        query = f'SELECT company_members.id as member_id,\
            invited,\
            companies.id as company_id,\
            companies.name as company_name,\
            companies.description as company_description,\
            companies.owner_id as owner_id\
            FROM company_members\
            INNER JOIN companies\
            ON company_members.company_id = companies.id\
            WHERE company_members.member_id = {self.user_id} AND\
            company_members.invited IS NOT NULL\
            LIMIT {self.limit} OFFSET {self.offset}'
        return query

    async def invites_counter(self):
        query = f'SELECT COUNT(*) as total_invites\
            FROM company_members\
            WHERE company_members.member_id = {self.user_id} AND\
            company_members.invited IS NOT NULL'
        return query


    async def all_companies(self):
        query = f'SELECT companies.id as company_id,\
            name as company_name,\
            description,\
            companies.created_at,\
            users.id as owner_id,\
            users.username as owner_usename\
            FROM companies\
            INNER JOIN users\
            ON companies.owner_id = users.id\
            WHERE companies.deleted_at IS NULL AND visible = True\
            LIMIT {self.limit} OFFSET {self.offset}'

        return query

    async def companies_counter(self):
        query = 'SELECT COUNT(*) as total_companies\
            FROM companies\
            WHERE companies.deleted_at IS NULL AND visible = True'
        return query





