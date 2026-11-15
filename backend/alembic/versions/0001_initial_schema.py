"""Initial schema: clients, cars, work_orders.

This is the schema the app used to create with Base.metadata.create_all().
Databases created that way have the tables but no alembic_version row, so
each table is only created if it is missing. That lets `alembic upgrade head`
adopt an existing database without losing data.

Revision ID: 0001
Revises:
Create Date: 2026-11-15
"""
import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    existing = set(sa.inspect(op.get_bind()).get_table_names())

    if "clients" not in existing:
        op.create_table(
            "clients",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("phone", sa.String(20), nullable=False),
            sa.Column("email", sa.String(100), nullable=False),
        )
        op.create_index("ix_clients_id", "clients", ["id"])

    if "cars" not in existing:
        op.create_table(
            "cars",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("client_id", sa.Integer(), nullable=False),
            sa.Column("brand", sa.String(50), nullable=False),
            sa.Column("model", sa.String(50), nullable=False),
            sa.Column("year", sa.Integer(), nullable=False),
            sa.Column("vin", sa.String(17), nullable=False),
            sa.ForeignKeyConstraint(["client_id"], ["clients.id"], name="cars_client_id_fkey"),
            sa.UniqueConstraint("vin", name="cars_vin_key"),
        )
        op.create_index("ix_cars_id", "cars", ["id"])

    if "work_orders" not in existing:
        op.create_table(
            "work_orders",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("car_id", sa.Integer(), nullable=False),
            sa.Column("description", sa.String(500), nullable=False),
            sa.Column("status", sa.String(20), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["car_id"], ["cars.id"], name="work_orders_car_id_fkey"),
        )
        op.create_index("ix_work_orders_id", "work_orders", ["id"])


def downgrade() -> None:
    op.drop_table("work_orders")
    op.drop_table("cars")
    op.drop_table("clients")
