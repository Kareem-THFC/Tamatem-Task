"""add gem balance

Adds the gem wallet the application now charges purchases against:

* ``users.gem_balance`` -- the live balance, defaulting to 500 gems so both
  existing accounts and new ones start with a usable amount.
* ``orders.gem_balance_after`` -- the balance the account was left with once
  the order was paid for, snapshotted so a receipt stays accurate after later
  purchases move the live balance.

Both columns use ``Numeric(10, 2)``, the type ``products.price`` already uses,
so a purchase is exact decimal subtraction.

Batch mode is used for the same reason as the two preceding revisions: SQLite
cannot add a check constraint in place, so Alembic rebuilds the table, and
``copy_from`` has to describe the table fully because check constraints are not
reflected and indexes are only recreated when the supplied definition declares
them.

Revision ID: c9a4b3e2d1f0
Revises: b7d2e8f1a4c3
Create Date: 2026-09-09 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9a4b3e2d1f0'
down_revision = 'b7d2e8f1a4c3'
branch_labels = None
depends_on = None


def _users_table(*extra) -> sa.Table:
    """Describe the users table, optionally with columns this revision adds."""
    return sa.Table(
        'users',
        sa.MetaData(),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_users_username', 'username', unique=True),
        sa.Index('ix_users_email', 'email', unique=True),
        *extra,
    )


def _orders_table(*extra) -> sa.Table:
    """Describe the orders table, optionally with columns this revision adds."""
    return sa.Table(
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
        *extra,
    )


def upgrade():
    # server_default is what lets a NOT NULL column be added to a table that
    # already has rows: batch mode copies the existing rows without naming the
    # new column, so the database fills it in. On users it is also the intended
    # permanent default, matching DEFAULT_GEM_BALANCE on the model.
    with op.batch_alter_table('users', copy_from=_users_table(), schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'gem_balance',
                sa.Numeric(precision=10, scale=2),
                nullable=False,
                server_default='500.00',
            )
        )
        batch_op.create_check_constraint(
            'ck_users_gem_balance_non_negative', 'gem_balance >= 0'
        )

    # Orders written before this revision have no recorded balance, so the
    # default here exists only to give those rows a value. New orders always
    # get theirs from the purchase itself.
    with op.batch_alter_table(
        'orders', copy_from=_orders_table(), schema=None
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                'gem_balance_after',
                sa.Numeric(precision=10, scale=2),
                nullable=False,
                server_default='0',
            )
        )
        batch_op.create_check_constraint(
            'ck_orders_gem_balance_after_non_negative', 'gem_balance_after >= 0'
        )


def downgrade():
    with op.batch_alter_table(
        'orders',
        copy_from=_orders_table(
            sa.Column(
                'gem_balance_after',
                sa.Numeric(precision=10, scale=2),
                nullable=False,
                server_default='0',
            ),
            sa.CheckConstraint(
                'gem_balance_after >= 0',
                name='ck_orders_gem_balance_after_non_negative',
            ),
        ),
        schema=None,
    ) as batch_op:
        batch_op.drop_constraint(
            'ck_orders_gem_balance_after_non_negative', type_='check'
        )
        batch_op.drop_column('gem_balance_after')

    with op.batch_alter_table(
        'users',
        copy_from=_users_table(
            sa.Column(
                'gem_balance',
                sa.Numeric(precision=10, scale=2),
                nullable=False,
                server_default='500.00',
            ),
            sa.CheckConstraint(
                'gem_balance >= 0', name='ck_users_gem_balance_non_negative'
            ),
        ),
        schema=None,
    ) as batch_op:
        batch_op.drop_constraint('ck_users_gem_balance_non_negative', type_='check')
        batch_op.drop_column('gem_balance')
