"""Agrega la columna imagen a valoracion (imagen adjunta a la reseña)

Revision ID: b7c1d2e3f4a5
Revises: 947d2fa9e9bc
Create Date: 2026-09-28 12:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7c1d2e3f4a5'
down_revision = '947d2fa9e9bc'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('valoracion', schema=None) as batch_op:
        batch_op.add_column(sa.Column('imagen', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('valoracion', schema=None) as batch_op:
        batch_op.drop_column('imagen')
