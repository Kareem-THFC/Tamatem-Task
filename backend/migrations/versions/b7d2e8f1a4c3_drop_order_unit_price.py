"""drop order unit price

A purchase is a single product, so unit_price always equalled total_price.
The duplicate column and its check constraint are removed, leaving total_price
as the single record of what the order cost.

Batch mode is used for the same reason as the previous revision: SQLite cannot
drop a column in place, and ``copy_from`` has to describe the table fully
because check constraints are not reflected and indexes are only recreated when
the supplied definition declares them.

Revision ID: b7d2e8f1a4c3
Revises: a3f1c2d4e5b6
Create Date: 2026-09-09 10:32:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7d2e8f1a4c3'
down_revision = 'a3f1c2d4e5b6'
branch_labels = None
depends_on = None

# The orders table exactly as the previous revision left it.
orders_with_unit_price = sa.Table(
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

orders_without_unit_price = sa.Table(
    'orders',
    sa.MetaData(),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column(
        'created_at',
        sa.DateTime(),
        server_default=sa.text('(CURRENT_TIMESTAMP)'),
        nullable=False,
    ),
    sa.CheckConstraint('total_price >= 0', name='ck_orders_total_price_non_negative'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id']),
    sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    sa.PrimaryKeyConstraint('id'),
    sa.Index('ix_orders_user_id', 'user_id'),
    sa.Index('ix_orders_product_id', 'product_id'),
)


def upgrade():
    with op.batch_alter_table(
        'orders', copy_from=orders_with_unit_price, schema=None
    ) as batch_op:
        batch_op.drop_constraint('ck_orders_unit_price_non_negative', type_='check')
        batch_op.drop_column('unit_price')


def downgrade():
    # server_default lets the NOT NULL column be added to a populated table; the
    # rows are then given their real value, which for a single-item order is the
    # total that was charged.
    with op.batch_alter_table(
        'orders', copy_from=orders_without_unit_price, schema=None
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                'unit_price',
                sa.Numeric(precision=10, scale=2),
                nullable=False,
                server_default='0',
            )
        )
        batch_op.create_check_constraint(
            'ck_orders_unit_price_non_negative', 'unit_price >= 0'
        )

    op.execute('UPDATE orders SET unit_price = total_price')
