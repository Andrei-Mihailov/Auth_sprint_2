"""Add partition to history

Revision ID: 37b4fdfe2f7e
Revises: 866d36e55d18
Create Date: 2024-05-03 08:29:55.540878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from db.postgres_db import Base


# revision identifiers, used by Alembic.
revision: str = '37b4fdfe2f7e'
down_revision: Union[str, None] = '866d36e55d18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""CREATE OR REPLACE FUNCTION func_partition_history()
                  RETURNS TRIGGER AS $$
                    DECLARE
                    current_date_part DATE;
                    current_date_part_text TEXT;
                    partition_table_name TEXT;
                    first_day_of_month DATE;
                    last_day_of_month DATE;
                    BEGIN
                    current_date_part := CAST(DATE_TRUNC('month', NEW.date_auth) AS DATE);
                    current_date_part_text := REGEXP_REPLACE(current_date_part::TEXT, '-','_','g');
                    partition_table_name := FORMAT('authentication_%s', current_date_part_text::TEXT);
                    IF (TO_REGCLASS(partition_table_name::TEXT) ISNULL) THEN
                        first_day_of_month := current_date_part;
                        last_day_of_month := current_date_part + '1 month'::INTERVAL;
                        EXECUTE FORMAT(
                        'CREATE TABLE %I ('
                        '  CHECK (date_auth >= DATE %L AND date_auth < DATE %L)'
                        ') INHERITS (authentication);'
                        , partition_table_name, first_day_of_month, last_day_of_month);
                        EXECUTE FORMAT(
                        'ALTER TABLE ONLY %1$I ADD CONSTRAINT %1$s__pkey PRIMARY KEY (id);'
                        , partition_table_name);
                        EXECUTE FORMAT(
                        'CREATE INDEX %1$s__date_auth ON %1$I (date_auth);'
                        , partition_table_name);
                    END IF;
                    EXECUTE FORMAT('INSERT INTO %I VALUES ($1.*)', partition_table_name) USING NEW;

                    RETURN NULL;
                    END;
                    $$
                    LANGUAGE plpgsql;
               """)
    op.execute("""CREATE TRIGGER trigger_partition_history    
                  BEFORE INSERT ON authentication
                  FOR EACH ROW EXECUTE FUNCTION func_partition_history();
               """)


def downgrade() -> None:
    op.execute("""DROP TRIGGER IF EXISTS trigger_partition_history ON authentication;
               """)
    op.execute("""DROP FUNCTION IF EXISTS func_partition_history();
               """)
