"""init alembic

Revision ID: 5434c5fc5066
Revises:
Create Date: 2023-12-15 18:47:16.975938

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5434c5fc5066"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "participant",
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("alias", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("telegram_id", sa.String(), nullable=True),
        sa.Column("phone_number", sa.LargeBinary(), nullable=True),
        sa.Column("need_to_fill_profile", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "potential_user",
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("code_expiration", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("email"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "booking",
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("time_start", sa.DateTime(), nullable=False),
        sa.Column("time_end", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["participant.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("booking")
    op.drop_table("potential_user")
    op.drop_table("participant")
    # ### end Alembic commands ###
