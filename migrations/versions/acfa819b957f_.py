"""empty message

Revision ID: acfa819b957f
Revises: e6c9a7cb8ba0
Create Date: 2020-05-28 16:58:39.713386

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acfa819b957f'
down_revision = 'e6c9a7cb8ba0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('phone', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'phone')
    # ### end Alembic commands ###
