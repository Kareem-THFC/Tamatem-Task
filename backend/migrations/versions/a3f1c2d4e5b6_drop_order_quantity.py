"""drop order quantity

A purchase is a single product, so quantity and its check constraint are no
longer part of the order.

SQLite cannot drop a column in place, so Alembic's batch mode is used: it
creates a new table with the desired shape, copies the rows across, drops the
old table and renames the new one. ``copy_from`` supplies the table definition
explicitly because SQLAlchemy does not reflect SQLite check constraints, and
without it the surviving price constraints would be silently lost when the
table is rebuilt. The indexes are declared for the same reason: batch mode
recreates only what the supplied definition describes.

Revision ID: a3f1c2d4e5b6
Revises: 1f54c39b25be
Create Date: 2026-09-09 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f1c2d4e5b6'
down_revision = '1f54c39b25be'
branch_labels = None
depends_on = None

metadata = sa.MetaData()

# The orders table exactly as the previous revision left it.
orders_with_quantity = sa.Table(
    'orders',
    metadata,
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column(
        'created_at',
        sa.DateTime(),
        server_default=sa.text('(CURRENT_TIMESTAMP)'),
        nullable=False,
    ),
    sa.CheckConstraint('quantity >= 1', name='ck_orders_quantity_positive'),
    sa.CheckConstraint('unit_price >= 0', name='ck_orders_unit_price_non_negative'),
    sa.CheckConstraint('total_price >= 0', name='ck_orders_total_price_non_negative'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id']),
    sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    sa.PrimaryKeyConstraint('id'),
    sa.Index('ix_orders_user_id', 'user_id'),
    sa.Index('ix_orders_product_id', 'product_id'),
)

orders_without_quantity = sa.Table(
    'orders',
    sa.MetaData(),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column(
        'created_at',
        sa.DateTime(),
        server_default=sa.text('(CURRENT_TIMESTAMP)'),
        nullable=False,
    ),
    sa.CheckConstraint('unit_price >= 0', name='ck_orders_unit_price_non_negative'),
    sa.CheckConstraint('total_price >= 0', name='ck_orders_total_price_non_negative'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id']),
    sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    sa.PrimaryKeyConstraint('id'),
    sa.Index('ix_orders_user_id', 'user_id'),
    sa.Index('ix_orders_product_id', 'product_id'),
)


def upgrade():
    with op.batch_alter_table(
        'orders', copy_from=orders_with_quantity, schema=None
    ) as batch_op:
        batch_op.drop_constraint('ck_orders_quantity_positive', type_='check')
        batch_op.drop_column('quantity')


def downgrade():
    # server_default backfills existing rows, which a NOT NULL column added to
    # a populated table otherwise could not satisfy.
    with op.batch_alter_table(
        'orders', copy_from=orders_without_quantity, schema=None
    ) as batch_op:
        batch_op.add_column(
            sa.Column('quantity', sa.Integer(), nullable=False, server_default='1')
        )
        batch_op.create_check_constraint('ck_orders_quantity_positive', 'quantity >= 1')
