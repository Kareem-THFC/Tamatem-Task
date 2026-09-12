"""Authentication business logic."""

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from app.errors.api_error import ApiError
from app.extensions import db
from app.models import User


def authenticate_user(identifier: str, password: str) -> User | None:
    """Return the matching user only when the supplied password is valid."""
    # Registration stores addresses lower-cased, so the email side of this
    # lookup is lower-cased to match. Comparing the stored column directly
    # rather than wrapping it in LOWER() keeps the unique index usable.
    #
    # A username keeps the capitalisation it was registered with, so that side
    # folds both operands instead. The unique index on User is declared over
    # the same lower(username) expression, so this stays an index lookup too.
    # One normalised value serves both comparisons.
    normalised = identifier.lower()

    user = User.query.filter(
        or_(User.email == normalised, func.lower(User.username) == normalised)
    ).first()

    if user is None or not user.check_password(password):
        return None

    return user


def register_user(username: str, email: str, password: str) -> User:
    """Create a new account, or raise a 409 when the identity is taken.

    The password arrives in plaintext and is hashed by ``set_password`` before
    the row is written, so the database never sees it. The starting gem balance
    is not set here: it comes from the column default on ``User``.
    """
    # Looked up before inserting so the response can name the field that
    # clashed, which a database error alone cannot tell us. Both sides are
    # matched the way their unique index is built: the email as stored, the
    # username case-folded, so "Buyer" cannot register alongside "buyer".
    normalised_username = username.lower()

    taken = User.query.filter(
        or_(func.lower(User.username) == normalised_username, User.email == email)
    ).first()

    if taken is not None:
        field, label = (
            ("username", "username")
            if taken.username.lower() == normalised_username
            else ("email", "email address")
        )
        message = f"That {label} is already registered."

        raise ApiError(
            "USER_ALREADY_EXISTS",
            message,
            409,
            [{"field": field, "message": message}],
        )

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()

        raise ApiError(
            "USER_ALREADY_EXISTS",
            "That username or email address is already registered.",
            409,
        ) from error

    return user
