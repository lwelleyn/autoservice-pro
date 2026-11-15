"""ON DELETE CASCADE on foreign keys, timezone-aware created_at.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-15
"""
import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

# (table, column, referenced table, constraint name)
FOREIGN_KEYS = [
    ("cars", "client_id", "clients", "cars_client_id_fkey"),
    ("work_orders", "car_id", "cars", "work_orders_car_id_fkey"),
]


def _existing_fk_names(table: str, column: str) -> list[str]:
    """Look the names up instead of assuming them: older databases may differ."""
    inspector = sa.inspect(op.get_bind())
    return [
        fk["name"]
        for fk in inspector.get_foreign_keys(table)
        if fk["constrained_columns"] == [column] and fk["name"]
    ]


def _replace_foreign_keys(ondelete: str | None) -> None:
    for table, column, referred, name in FOREIGN_KEYS:
        old_names = _existing_fk_names(table, column)
        with op.batch_alter_table(table) as batch:
            for old_name in old_names:
                batch.drop_constraint(old_name, type_="foreignkey")
            batch.create_foreign_key(name, referred, [column], ["id"], ondelete=ondelete)


def upgrade() -> None:
    _replace_foreign_keys(ondelete="CASCADE")
    with op.batch_alter_table("work_orders") as batch:
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=True,
            # Existing values were written with datetime.utcnow(), i.e. naive UTC.
            postgresql_using="created_at AT TIME ZONE 'UTC'",
        )


def downgrade() -> None:
    with op.batch_alter_table("work_orders") as batch:
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=True,
            postgresql_using="created_at AT TIME ZONE 'UTC'",
        )
    _replace_foreign_keys(ondelete=None)
