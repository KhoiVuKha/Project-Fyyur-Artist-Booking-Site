"""empty message

Revision ID: 5137d7875cb6
Revises: ec792141d7ac
Create Date: 2023-03-07 23:25:42.609617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5137d7875cb6'
down_revision = 'ec792141d7ac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website_link', sa.String(length=200), nullable=True))
    op.drop_column('Venue', 'website')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website', sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'website_link')
    # ### end Alembic commands ###
