"""
Add back new leads model

Revision ID: 546db5df3f0
Revises: a21cdbde22
Create Date: 2015-07-20 19:28:16.287954
"""

# revision identifiers, used by Alembic.
revision = '546db5df3f0'
down_revision = 'a21cdbde22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'lead_sources',
    sa.Column('id', sa.Integer(), nullable=False), sa.Column('name',
                                                             sa.Unicode(length=255),
                                                             nullable=False),
        sa.Column('category', sa.String(length=6), nullable=False),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.Column('updated_by_id', sa.Integer(), nullable=False),
        sa.Column('updated_time', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'],
                                name=op.f('fk_lead_sources_created_by_id')),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'],
                                name=op.f('fk_lead_sources_updated_by_id')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_lead_sources')),
        mysql_engine='InnoDB')
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=False),
        sa.Column('description', sa.UnicodeText(), nullable=False),
        sa.Column('contact', sa.Unicode(length=255), nullable=False),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('last_contact_time', sa.DateTime(), nullable=True),
        sa.Column('next_contact_time', sa.DateTime(), nullable=False),
        sa.Column('stage', sa.String(length=4), nullable=False),
        sa.Column('eval_time', sa.DateTime(), nullable=True),
        sa.Column('qual_time', sa.DateTime(), nullable=True),
        sa.Column('nego_time', sa.DateTime(), nullable=True),
        sa.Column('prel_time', sa.DateTime(), nullable=True),
        sa.Column('dead_time', sa.DateTime(), nullable=True),
        sa.Column('live_time', sa.DateTime(), nullable=True),
        sa.Column('dead_reason', sa.String(length=7), nullable=True),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('is_inbound', sa.Boolean(), nullable=False),
        sa.Column('contact_channel', sa.String(length=6), nullable=False),
        sa.Column('initial_est_launch_time', sa.DateTime(), nullable=True),
        sa.Column('initial_est_tier', sa.String(length=4), nullable=False),
        sa.Column('initial_est_six_month_sales', sa.Integer(), nullable=False),
        sa.Column('initial_est_six_month_percentage', sa.Integer(), nullable=False),
        sa.Column('refined_est_launch_time', sa.DateTime(), nullable=True),
        sa.Column('refined_est_tier', sa.String(length=4), nullable=False),
        sa.Column('refined_est_six_month_sales', sa.Integer(), nullable=False),
        sa.Column('refined_est_six_month_percentage', sa.Integer(), nullable=False),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.Column('updated_by_id', sa.Integer(), nullable=False),
        sa.Column('updated_time', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'],
                                name=op.f('fk_leads_assigned_to_id')),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'],
                                name=op.f('fk_leads_created_by_id')),
        sa.ForeignKeyConstraint(['source_id'], ['lead_sources.id'],
                                name=op.f('fk_leads_source_id')),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'],
                                name=op.f('fk_leads_updated_by_id')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_leads')),
        mysql_engine='InnoDB'
    )
    op.create_table(
        'leads_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('body', sa.UnicodeText(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'],
                                name=op.f('fk_leads_comments_created_by_id')),
        sa.ForeignKeyConstraint(['source_id'], ['leads.id'],
                                name=op.f('fk_leads_comments_source_id')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_leads_comments')),
        mysql_engine='InnoDB'
    )


def downgrade():
    op.drop_table('leads_comments')
    op.drop_table('leads')
    op.drop_table('lead_sources')
