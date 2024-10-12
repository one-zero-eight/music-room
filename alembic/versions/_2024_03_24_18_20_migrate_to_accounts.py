"""migrate to accounts

Revision ID: ae811bbde3f1
Revises: e4798976bd79
Create Date: 2024-03-24 18:20:01.601659

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ae811bbde3f1"
down_revision: Union[str, None] = "e4798976bd79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("potential_user")
    op.add_column("booking", sa.Column("user_id", sa.Integer(), nullable=False))
    op.drop_constraint("booking_participant_id_fkey", "booking", type_="foreignkey")
    op.create_foreign_key(None, "booking", "participant", ["user_id"], ["id"])
    op.drop_column("booking", "participant_id")
    op.alter_column(
        "participant",
        "telegram_id",
        existing_type=sa.VARCHAR(),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="telegram_id::integer",
    )
    op.drop_column("participant", "need_to_fill_profile")
    op.drop_column("participant", "phone_number")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("participant", sa.Column("phone_number", postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.add_column("participant", sa.Column("need_to_fill_profile", sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.alter_column(
        "participant", "telegram_id", existing_type=sa.Integer(), type_=sa.VARCHAR(), existing_nullable=True
    )
    op.add_column("booking", sa.Column("participant_id", sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, "booking", type_="foreignkey")
    op.create_foreign_key("booking_participant_id_fkey", "booking", "participant", ["participant_id"], ["id"])
    op.drop_column("booking", "user_id")
    op.create_table(
        "potential_user",
        sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("code", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("code_expiration", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id", name="potential_user_pkey"),
    )
    # ### end Alembic commands ###
