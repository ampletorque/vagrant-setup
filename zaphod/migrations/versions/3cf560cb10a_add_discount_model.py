from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
"""
Add discount model

Revision ID: 3cf560cb10a
Revises: 2f6abf8c3e1
Create Date: 2015-04-11 20:45:01.574643
"""

# revision identifiers, used by Alembic.
revision = '3cf560cb10a'
down_revision = '2f6abf8c3e1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'discounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('rate', sa.Numeric(precision=6, scale=4),
                  nullable=False),
        sa.Column('description', sa.Unicode(length=255),
                  nullable=False),
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('updated_time', sa.DateTime(), nullable=False),
        sa.Column('updated_by_id', sa.Integer(), nullable=False),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'],
                                name=op.f('fk_discounts_created_by_id')),
        sa.ForeignKeyConstraint(['creator_id'], ['creators.node_id'],
                                name=op.f('fk_discounts_creator_id')),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'],
                                name=op.f('fk_discounts_updated_by_id')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_discounts')),
        mysql_engine='InnoDB'
    )
    op.create_table(
        'discount_users',
        sa.Column('discount_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['discount_id'], ['discounts.id'],
                                name=op.f('fk_discount_users_discount_id')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'],
                                name=op.f('fk_discount_users_user_id')),
        sa.PrimaryKeyConstraint('discount_id', 'user_id',
                                name=op.f('pk_discount_users')),
        mysql_engine='InnoDB'
    )
    op.create_table(
        'discount_products',
        sa.Column('discount_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['discount_id'], ['discounts.id'],
                                name=op.f('fk_discount_products_discount_id')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'],
                                name=op.f('fk_discount_products_product_id')),
        sa.PrimaryKeyConstraint('discount_id', 'product_id',
                                name=op.f('pk_discount_products')),
        mysql_engine='InnoDB'
    )


def downgrade():
    op.drop_table('discount_products')
    op.drop_table('discount_users')
    op.drop_table('discounts')
