"""Add partition to auth

Revision ID: 65a4e8f17754
Revises: 866d36e55d18
Create Date: 2024-05-05 05:29:22.510713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from db.postgres_db import Base


# revision identifiers, used by Alembic.
revision: str = '65a4e8f17754'
down_revision: Union[str, None] = '866d36e55d18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS authentication CASCADE;")
    op.execute("""CREATE TABLE public.authentication (
                            id uuid NOT NULL,
                            user_id uuid NOT NULL,
                            user_agent character varying(255) NOT NULL,
                            date_auth timestamp without time zone NOT NULL
                    ) PARTITION BY RANGE (date_auth);
               """)
    
    op.execute("""ALTER TABLE public.authentication
                  ADD CONSTRAINT authentication_user_id_fkey 
                  FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
               """)
    
    op.execute("CREATE SCHEMA IF NOT EXISTS partman;")
    op.execute("CREATE EXTENSION IF NOT EXISTS  pg_partman WITH SCHEMA partman;")

    op.execute("""SELECT partman.create_parent( p_parent_table => 'public.authentication',
                        p_control => 'date_auth',
                        p_type => 'native',
                        p_interval=> 'monthly',
                        p_start_partition => (now() - interval '3 month')::text,
                        p_premake => 10);""") 


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS authentication CASCADE;")
    op.execute("DROP EXTENSION IF EXISTS pg_partman;")
    op.execute("DROP SCHEMA IF EXISTS partman CASCADE;")
    op.create_table(
        "authentication",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("user_agent", sa.String(length=255), nullable=False),
        sa.Column("date_auth", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
