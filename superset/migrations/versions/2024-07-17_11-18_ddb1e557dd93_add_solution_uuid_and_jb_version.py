# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""add solution_uuid and jb_version

Revision ID: ddb1e557dd93
Revises: 346d233b7fc2
Create Date: 2024-07-17 11:18:33.257574

"""

# revision identifiers, used by Alembic.
revision = 'ddb1e557dd93'
down_revision = '346d233b7fc2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

def has_column(table_name, column_name, bind):
    inspector = Inspector.from_engine(bind)
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    return column_name in columns

def upgrade():
    bind = op.get_bind()
    
    with op.batch_alter_table('ab_user') as batch_op:
        if not has_column('ab_user', 'solution_uuid', bind):
            batch_op.add_column(sa.Column('solution_uuid', sa.String(), nullable=True))
        
        if not has_column('ab_user', 'jabberbrain_version', bind):
            batch_op.add_column(sa.Column('jabberbrain_version', sa.String(), nullable=True))

def downgrade():
    bind = op.get_bind()

    with op.batch_alter_table('ab_user') as batch_op:
        if has_column('ab_user', 'jabberbrain_version', bind):
            batch_op.drop_column('jabberbrain_version')

        if has_column('ab_user', 'solution_uuid', bind):
            batch_op.drop_column('solution_uuid')
