"""Update data structure

Revision ID: 81b8fbe20172
Revises: 33eb61b5c2a0
Create Date: 2020-05-26 22:04:10.375925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81b8fbe20172'
down_revision = '33eb61b5c2a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('venue_id', sa.Integer(), nullable=False),
                    sa.Column('artist_id', sa.Integer(), nullable=False),
                    sa.Column('start_time', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
                    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('Artist', sa.Column(
        'seeking_description', sa.String(), nullable=True))
    op.add_column('Artist', sa.Column(
        'seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column(
        'website', sa.String(length=120), nullable=True))
    op.alter_column('Artist', 'name',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.add_column('Venue', sa.Column(
        'genres', sa.ARRAY(sa.String()), nullable=False))
    op.add_column('Venue', sa.Column('seeking_description',
                                     sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column(
        'seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column(
        'website', sa.String(length=120), nullable=True))
    op.alter_column('Venue', 'address',
                    existing_type=sa.VARCHAR(length=120),
                    nullable=False)
    op.alter_column('Venue', 'city',
                    existing_type=sa.VARCHAR(length=120),
                    nullable=False)
    op.alter_column('Venue', 'name',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('Venue', 'state',
                    existing_type=sa.VARCHAR(length=120),
                    nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'state',
                    existing_type=sa.VARCHAR(length=120),
                    nullable=True)
    op.alter_column('Venue', 'name',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('Venue', 'city',
                    existing_type=sa.VARCHAR(length=120),
                    nullable=True)
    op.alter_column('Venue', 'address',
                    existing_type=sa.VARCHAR(length=120),
                    nullable=True)
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'genres')
    op.alter_column('Artist', 'name',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'seeking_description')
    op.drop_table('Show')
    # ### end Alembic commands ###
