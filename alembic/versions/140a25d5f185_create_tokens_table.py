"""create tokens table

Revision ID: 140a25d5f185
Revises: 
Create Date: 2020-12-12 01:44:28.195736

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.engine.reflection import Inspector
from flask_sqlalchemy import SQLAlchemy


# revision identifiers, used by Alembic.
revision = '140a25d5f185'
down_revision = None
branch_labels = None
depends_on = None

db = SQLAlchemy()


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'ips' not in tables:
        op.create_table(
            'ips',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('address', sa.String(255), nullable=True)
        )

    if 'tokens' not in tables:
        op.create_table(
            'tokens',
            sa.Column('name', String(255), primary_key=True),
            sa.Column('expiration_date', DateTime, nullable=True),
            sa.Column('max_usage', Integer, default=1),
            sa.Column('used', Integer, default=0),
            sa.Column('disabled', Boolean, default=False),
            sa.Column('ips', Integer, ForeignKey('association.id'))
        )
    else:
        try:
            with op.batch_alter_table('tokens') as batch_op:
                batch_op.alter_column('ex_date', new_column_name='expiration_date', nullable=True)
                batch_op.alter_column('one_time', new_column_name='max_usage')

                batch_op.add_column(
                    Column('disabled', Boolean, default=False)
                )
        except KeyError:
            pass


    if 'association' not in tables:
        op.create_table(
        'association', db.Model.metadata,
            Column('ips', String, ForeignKey('ips.address'), primary_key=True),
            Column('tokens', Integer, ForeignKey('tokens.name'), primary_key=True)
        )   
    
    op.execute("update tokens set expiration_date=null where expiration_date='None'")



def downgrade():
    op.alter_column('tokens', 'expiration_date', new_column_name='ex_date')
    op.alter_column('tokens', 'max_usage', new_column_name='one_time')
