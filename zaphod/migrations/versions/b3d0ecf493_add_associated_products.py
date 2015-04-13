from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
"""
Add associated products

Revision ID: b3d0ecf493
Revises: 68ecb03a15
Create Date: 2015-04-12 21:11:25.624729
"""

# revision identifiers, used by Alembic.
revision = 'b3d0ecf493'
down_revision = '68ecb03a15'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'associated_products',
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('dest_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['dest_id'], ['products.id'],
                                name=op.f('fk_associated_products_dest_id')),
        sa.ForeignKeyConstraint(['source_id'], ['products.id'],
                                name=op.f('fk_associated_products_source_id')),
        sa.PrimaryKeyConstraint('source_id', 'dest_id',
                                name=op.f('pk_associated_products')),
        mysql_engine='InnoDB'
    )


def downgrade():
    op.drop_table('associated_products')
