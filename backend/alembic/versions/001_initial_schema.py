"""Provide argument to "down_revision" in '%(slug)s'

Revision ID: <generated>
Revises:
Create Date: <date>

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'init'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === 租户与用户 ===
    op.create_table('tenant',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('industry', sa.String(50)),
        sa.Column('contact_email', sa.String(100)),
        sa.Column('phone', sa.String(20)),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('plan', sa.String(20), server_default='free'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_table('user',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('nickname', sa.String(50)),
        sa.Column('avatar', sa.String(255)),
        sa.Column('gender', sa.Integer),
        sa.Column('birthday', sa.DateTime),
        sa.Column('region', sa.String(50)),
        sa.Column('membership_level', sa.String(20), server_default='regular'),
        sa.Column('points', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_table('admin_user',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('email', sa.String(100)),
        sa.Column('avatar', sa.String(255)),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )

    # === RBAC ===
    op.create_table('permission',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('code', sa.String(100), unique=True, nullable=False),
        sa.Column('resource', sa.String(50)),
        sa.Column('action', sa.String(50)),
        sa.Column('description', sa.String(255)),
    )
    op.create_table('role',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('code', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_table('role_permission',
        sa.Column('role_id', sa.String(36), sa.ForeignKey('role.id'), primary_key=True),
        sa.Column('permission_id', sa.String(36), sa.ForeignKey('permission.id'), primary_key=True),
    )
    op.create_table('user_role',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('role_id', sa.String(36), nullable=False),
    )
    op.create_table('menu',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('parent_id', sa.String(36)),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('path', sa.String(100)),
        sa.Column('component', sa.String(100)),
        sa.Column('icon', sa.String(50)),
        sa.Column('sort_order', sa.Integer, server_default='0'),
        sa.Column('visible', sa.Integer, server_default='1'),
        sa.Column('type', sa.Integer, server_default='1'),
        sa.Column('created_at', sa.DateTime()),
    )

    # === 会话与消息 ===
    op.create_table('session',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('channel', sa.String(20), server_default='web'),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('current_agent_type', sa.String(20), server_default='ai'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_table('message',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('session.id'), nullable=False),
        sa.Column('sender_type', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('content_type', sa.String(20), server_default='text'),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_table('satisfaction',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('session.id'), nullable=False),
        sa.Column('score', sa.Integer, server_default='5'),
        sa.Column('comment', sa.Text),
        sa.Column('created_at', sa.DateTime()),
    )

    # === 工单系统 ===
    op.create_table('ticket',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('session.id')),
        sa.Column('creator_type', sa.String(20), server_default='user'),
        sa.Column('type', sa.String(50), server_default='consultation'),
        sa.Column('priority', sa.String(20), server_default='normal'),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('assigned_to', sa.String(36)),
        sa.Column('sla_deadline', sa.DateTime),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_table('ticket_comment',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('ticket_id', sa.String(36), sa.ForeignKey('ticket.id'), nullable=False),
        sa.Column('sender_type', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime()),
    )

    # === 知识库 ===
    op.create_table('knowledge_entry',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('category', sa.String(50), server_default='default'),
        sa.Column('tags', sa.String(500)),
        sa.Column('vector_id', sa.String(100)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_table('file_conversion',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('original_file', sa.String(500)),
        sa.Column('converted_md', sa.Text),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('created_by', sa.String(36)),
        sa.Column('created_at', sa.DateTime()),
    )

    # === 系统与配置 ===
    op.create_table('system_config',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_table('translation',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('language', sa.String(20), nullable=False),
        sa.Column('key', sa.String(200), nullable=False),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('updated_at', sa.DateTime()),
    )

    # === 统计与分析 ===
    op.create_table('agent_efficiency_log',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('agent_type', sa.String(20), server_default='ai'),
        sa.Column('agent_id', sa.String(36)),
        sa.Column('first_response_time', sa.Float),
        sa.Column('avg_response_time', sa.Float),
        sa.Column('session_count', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_table('rating_record',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('agent_type', sa.String(20), server_default='ai'),
        sa.Column('agent_id', sa.String(36)),
        sa.Column('score', sa.Integer, nullable=False),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('session.id')),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_table('event_log',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36)),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_data', sa.String(2000)),
        sa.Column('ip', sa.String(45)),
        sa.Column('created_at', sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table('event_log')
    op.drop_table('rating_record')
    op.drop_table('agent_efficiency_log')
    op.drop_table('translation')
    op.drop_table('system_config')
    op.drop_table('file_conversion')
    op.drop_table('knowledge_entry')
    op.drop_table('ticket_comment')
    op.drop_table('ticket')
    op.drop_table('satisfaction')
    op.drop_table('message')
    op.drop_table('session')
    op.drop_table('menu')
    op.drop_table('user_role')
    op.drop_table('role_permission')
    op.drop_table('role')
    op.drop_table('permission')
    op.drop_table('admin_user')
    op.drop_table('user')
    op.drop_table('tenant')
