"""one order per user per product

An account may own a given product once, so ``orders`` gains a unique
constraint on ``(user_id, product_id)``.

The service already refuses a repeat purchase before charging anything, but two
simultaneous requests could both pass that check before either insert lands.
Only the database can rule that out, which is why the constraint exists as well
as the check in ``order_service.create_order``.

Batch mode is used for the same reason as the preceding revisions: SQLite
cannot add a constraint in place, so Alembic rebuilds the table, and
``copy_from`` has to describe the table fully because check constraints are not
reflected and indexes are only recreated when the supplied definition declares
them.

Revision ID: d5e8c1a7b204
Revises: c9a4b3e2d1f0
Create Date: 2026-09-11 12:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5e8c1a7b204'
down_revision = 'c9a4b3e2d1f0'
branch_labels = None
depends_on = None


def _orders_table(*extra) -> sa.Table:
    """Describe the orders table as it stands before this revision."""
    return sa.Table(
        'orders',
        sa.MetaData(),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            'gem_balance_after',
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default='0',
        ),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.CheckConstraint(
            'total_price >= 0', name='ck_orders_total_price_non_negative'
        ),
        sa.CheckConstraint(
            'gem_balance_after >= 0',
            name='ck_orders_gem_balance_after_non_negative',
        ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_orders_user_id', 'user_id'),
        sa.Index('ix_orders_product_id', 'product_id'),
        *extra,
    )


def upgrade():
    # Any pre-existing duplicate would make this fail, which is the correct
    # outcome: the data would contradict the rule being introduced, and that
    # should stop the migration rather than be silently discarded.
    with op.batch_alter_table(
        'orders', copy_from=_orders_table(), schema=None
    ) as batch_op:
        batch_op.create_unique_constraint(
            'uq_orders_user_product', ['user_id', 'product_id']
        )


def downgrade():
    with op.batch_alter_table(
        'orders',
        copy_from=_orders_table(
            sa.UniqueConstraint(
                'user_id', 'product_id', name='uq_orders_user_product'
            )
        ),
        schema=None,
    ) as batch_op:
        batch_op.drop_constraint('uq_orders_user_product', type_='unique')
