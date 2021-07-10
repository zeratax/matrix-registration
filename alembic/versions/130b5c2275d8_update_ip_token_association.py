'''update ip token association

Revision ID: 130b5c2275d8
Revises: 140a25d5f185
Create Date: 2021-07-10 20:40:46.937634

'''
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.engine.reflection import Inspector
from flask_sqlalchemy import SQLAlchemy

# revision identifiers, used by Alembic.
revision = '130b5c2275d8'
down_revision = '140a25d5f185'
branch_labels = None
depends_on = None

db = SQLAlchemy()
conn = op.get_bind()

def upgrade():
        ips = conn.execute('select id, address from ips').fetchall()
        associations = conn.execute('select ips, tokens from association').fetchall()

        final_associations = []
        for association in associations:
            association_ip, association_token = association
            for ip in ips:
                id, ip_address = ip
                if ip_address == association_ip:
                    final_associations.append({'ips': id, 'tokens': association_token})

        op.drop_table('association')

        association = op.create_table(
            'association', db.Model.metadata,
                Column('ips', Integer, ForeignKey('ips.id'), primary_key=True),
                Column('tokens', String(255), ForeignKey('tokens.name'), primary_key=True)
        )   


        op.bulk_insert(association, final_associations)

        

def downgrade():
    ips = conn.execute('select id, address from ips').fetchall()
    associations = conn.execute('select ips, tokens from association').fetchall()

    final_associations = []
    for association in associations:
        association_ip, association_token = association
        for ip in ips:
            id, ip_address = ip
            if id == association_ip:
                final_associations.append({'ips': ip_address, 'tokens': association_token})

    op.drop_table('association')

    association = op.create_table(
        'association', db.Model.metadata,
            Column('ips', String(255), ForeignKey('ips.address'), primary_key=True),
            Column('tokens', String(255), ForeignKey('tokens.name'), primary_key=True)
    )   


    op.bulk_insert(association, final_associations)
