"""Add tweetchi Status

Revision ID: b1896cb4e73
Revises: 3c6bb84e555a
Create Date: 2012-08-20 21:26:36.902694

"""

# revision identifiers, used by Alembic.
from datetime import datetime

import sqlalchemy as db
from alembic import op


revision = 'b1896cb4e73'
down_revision = '3c6bb84e555a'


def upgrade():
    op.create_table(
        'tweetchi_status',
        db.Column('id', db.Integer, primary_key=True),
        db.Column('created_at', db.DateTime,
                  default=datetime.utcnow, nullable=False),
        db.Column('updated_at', db.DateTime,
                  onupdate=datetime.utcnow, default=datetime.utcnow),
        db.Column('id_str', db.String(20), nullable=False, unique=True),
        db.Column('text', db.String(200), nullable=False),
        db.Column('in_reply_id_str', db.String(20)),
        db.Column('screen_name', db.String(30), nullable=False),
        db.Column('myself', db.Boolean, default=False),
    )


def downgrade():
    op.drop_table('tweetchi_status')
