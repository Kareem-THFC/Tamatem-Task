"""User database model."""

from decimal import Decimal

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

# Every new account starts with this many gems. Defined here, next to the
# column that uses it, so the value the API hands out and the value the
# database writes can never drift apart.
DEFAULT_GEM_BALANCE = Decimal("500.00")


class User(db.Model):
    """A customer who can authenticate and place orders."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    gem_balance = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=DEFAULT_GEM_BALANCE,
        server_default="500.00",
    )

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    __table_args__ = (
        db.CheckConstraint(
            "gem_balance >= 0", name="ck_users_gem_balance_non_negative"
        ),
        db.Index("uq_users_username_lower", db.func.lower(username), unique=True),
    )

    orders = db.relationship("Order", back_populates="user")

    def to_dict(self) -> dict:
        """Return only the fields that are safe to expose through the API.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "gem_balance": str(self.gem_balance),
        }

    def set_password(self, password: str) -> None:
        """Hash a plaintext password before it is stored in the database."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Safely compare a plaintext password with the stored hash."""
        return check_password_hash(self.password_hash, password)
