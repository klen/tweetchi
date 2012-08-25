"""status_add_reply_name

Revision ID: 372e792b9d13
Revises: b1896cb4e73
Create Date: 2012-08-25 14:33:20.424489

"""

# revision identifiers, used by Alembic.
revision = '372e792b9d13'
down_revision = 'b1896cb4e73'

from alembic import op
import sqlalchemy as db


def upgrade():
    op.add_column('tweetchi_status',
                  db.Column('in_reply_to_screen_name', db.String(30))
                  )


def downgrade():
    op.drop_column('tweetchi_status', 'in_reply_to_screen_name')
