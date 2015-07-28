"""
Remove existing leads model

Revision ID: a21cdbde22
Revises: 8505303ed7
Create Date: 2015-07-20 19:27:26.451133
"""

# revision identifiers, used by Alembic.
revision = 'a21cdbde22'
down_revision = '8505303ed7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.drop_table('leads_comments')
    op.drop_table('leads')
    op.drop_table('lead_sources')


def downgrade():
    op.create_table('lead_sources',
                    sa.Column('id', mysql.INTEGER(display_width=11),
                              nullable=False),
                    sa.Column('name', mysql.VARCHAR(length=255),
                              nullable=False),
                    sa.Column('category', mysql.VARCHAR(length=6),
                              nullable=False),
                    sa.Column('created_by_id', mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=False),
                    sa.Column('created_time', mysql.DATETIME(),
                              nullable=False),
                    sa.Column('updated_by_id', mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=False),
                    sa.Column('updated_time', mysql.DATETIME(),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_default_charset='utf8',
                    mysql_engine='InnoDB')
    op.create_table('leads',
                    sa.Column('id', mysql.INTEGER(display_width=11),
                              nullable=False),
                    sa.Column('name', mysql.VARCHAR(length=255),
                              nullable=False),
                    sa.Column('description', mysql.TEXT(), nullable=False),
                    sa.Column('status', mysql.VARCHAR(length=4),
                              nullable=False),
                    sa.Column('opp_time', mysql.DATETIME(), nullable=True),
                    sa.Column('cred_time', mysql.DATETIME(), nullable=True),
                    sa.Column('prel_time', mysql.DATETIME(), nullable=True),
                    sa.Column('dead_time', mysql.DATETIME(), nullable=True),
                    sa.Column('live_time', mysql.DATETIME(), nullable=True),
                    sa.Column('assigned_to_id',
                              mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=True),
                    sa.Column('referred_by_id',
                              mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=True),
                    sa.Column('source_id', mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=False),
                    sa.Column('contact_point', mysql.VARCHAR(length=6),
                              nullable=False),
                    sa.Column('last_contact_time', mysql.DATETIME(),
                              nullable=True),
                    sa.Column('next_contact_time', mysql.DATETIME(),
                              nullable=False),
                    sa.Column('estimated_launch_time', mysql.DATETIME(),
                              nullable=True),
                    sa.Column('campaign_duration_days',
                              mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=True),
                    sa.Column('email', mysql.VARCHAR(length=255),
                              nullable=False),
                    sa.Column('phone', mysql.VARCHAR(length=255),
                              nullable=False),
                    sa.Column('person', mysql.VARCHAR(length=255),
                              nullable=False),
                    sa.Column('updated_time', mysql.DATETIME(),
                              nullable=False),
                    sa.Column('updated_by_id', mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=False),
                    sa.Column('created_time', mysql.DATETIME(),
                              nullable=False),
                    sa.Column('created_by_id', mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=False),
                    sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'],
                                            name='leads_ibfk_1'),
                    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'],
                                            name='leads_ibfk_5'),
                    sa.ForeignKeyConstraint(['referred_by_id'], ['users.id'],
                                            name='leads_ibfk_2'),
                    sa.ForeignKeyConstraint(['source_id'], ['lead_sources.id'],
                                            name='leads_ibfk_3'),
                    sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'],
                                            name='leads_ibfk_4'),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_default_charset='utf8',
                    mysql_engine='InnoDB')
    op.create_table('leads_comments',
                    sa.Column('id', mysql.INTEGER(display_width=11),
                              nullable=False),
                    sa.Column('source_id', mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=False),
                    sa.Column('created_time', mysql.DATETIME(),
                              nullable=False),
                    sa.Column('created_by_id', mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=False),
                    sa.Column('body', mysql.TEXT(), nullable=False),
                    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'],
                                            name='leads_comments_ibfk_2'),
                    sa.ForeignKeyConstraint(['source_id'], ['leads.id'],
                                            name='leads_comments_ibfk_1'),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_default_charset='utf8',
                    mysql_engine='InnoDB')
