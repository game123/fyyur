"""empty message

Revision ID: 6545d5b5ddb1
Revises: 81b8fbe20172
Create Date: 2020-05-28 00:43:50.989123

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6545d5b5ddb1'
down_revision = '81b8fbe20172'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('test', sa.String(length=120), nullable=True))
    op.alter_column('Venue', 'genres',
               existing_type=postgresql.ARRAY(sa.VARCHAR()),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'genres',
               existing_type=postgresql.ARRAY(sa.VARCHAR()),
               nullable=False)
    op.drop_column('Venue', 'test')
    # ### end Alembic commands ###