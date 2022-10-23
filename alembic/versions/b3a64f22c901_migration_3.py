"""migration_3

Revision ID: b3a64f22c901
Revises: a8400094a879
Create Date: 2022-10-23 09:56:07.153441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3a64f22c901'
down_revision = 'a8400094a879'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('companies', sa.Column('name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('companies', 'name')
    # ### end Alembic commands ###
