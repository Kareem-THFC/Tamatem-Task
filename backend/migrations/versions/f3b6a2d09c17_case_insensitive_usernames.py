"""case-insensitive usernames

Two accounts may not have usernames that differ only by capitalisation, so
``users`` gains a unique index over ``lower(username)``.

The column keeps its own unique index. That one is now implied by this one --
anything it would reject this rejects too -- but removing it would mean
rebuilding the table under batch mode, which is a great deal of machinery for
an index that costs a write and documents the guarantee on the column itself.

An expression index rather than a lower-cased column: the name is shown back to
its owner in the UI, so the capitalisation they typed is worth keeping. Only
the comparison is case-insensitive, which is also how ``auth_service`` queries
it.

Revision ID: f3b6a2d09c17
Revises: d5e8c1a7b204
Create Date: 2026-09-11 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3b6a2d09c17'
down_revision = 'd5e8c1a7b204'
branch_labels = None
depends_on = None


def upgrade():
    # Existing usernames differing only by case would make this fail, which is
    # the correct outcome for the same reason as the order constraint in
    # d5e8c1a7b204: the data contradicts the rule being introduced, and that is
    # a decision for whoever owns the data, not something to resolve silently.
    op.create_index(
        'uq_users_username_lower',
        'users',
        [sa.text('lower(username)')],
        unique=True,
    )


def downgrade():
    op.drop_index('uq_users_username_lower', table_name='users')
