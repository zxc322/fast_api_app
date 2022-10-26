"""migration_3

Revision ID: 12f00cea1b55
Revises: 8e650c385b4f
Create Date: 2022-10-24 15:42:48.179320

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12f00cea1b55'
down_revision = '8e650c385b4f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company_members', sa.Column('is_company_admin', sa.Boolean(), nullable=True))
    op.drop_column('company_members', 'is_admin')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company_members', sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('company_members', 'is_company_admin')
    # ### end Alembic commands ###