"""Init

Revision ID: 6b5c10d860ff
Revises: 8742eada824a
Create Date: 2024-01-15 09:02:43.735357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b5c10d860ff'
down_revision: Union[str, None] = '8742eada824a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('f_name', sa.String(length=50), nullable=False))
    op.add_column('contacts', sa.Column('l_name', sa.String(length=50), nullable=False))
    op.drop_index('ix_contacts_name', table_name='contacts')
    op.create_index(op.f('ix_contacts_f_name'), 'contacts', ['f_name'], unique=False)
    op.create_index(op.f('ix_contacts_l_name'), 'contacts', ['l_name'], unique=False)
    op.drop_column('contacts', 'name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_contacts_l_name'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_f_name'), table_name='contacts')
    op.create_index('ix_contacts_name', 'contacts', ['name'], unique=False)
    op.drop_column('contacts', 'l_name')
    op.drop_column('contacts', 'f_name')
    # ### end Alembic commands ###
