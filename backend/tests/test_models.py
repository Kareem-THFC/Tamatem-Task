"""Persistence tests for the core database models."""

from decimal import Decimal

from app.extensions import db
from app.models import Order, Product, User
from app.models.user import DEFAULT_GEM_BALANCE


def test_order_links_a_user_and_product(app):
    with app.app_context():
        user = User(username="demo-user", email="demo@example.com")
        user.set_password("correct-password")

        product = Product(
            id=1,
            title="Sword of Valor",
            description="A legendary sword with magical powers",
            price=Decimal("150.00"),
            location="JO",
        )
        order = Order(
            user=user,
            product=product,
            total_price=Decimal("150.00"),
            gem_balance_after=Decimal("350.00"),
        )

        db.session.add(order)
        db.session.commit()

        saved_order = db.session.get(Order, order.id)

        assert saved_order.user.username == "demo-user"
        assert saved_order.product.title == "Sword of Valor"
        assert saved_order.total_price == Decimal("150.00")
        assert saved_order.gem_balance_after == Decimal("350.00")


def test_a_new_user_starts_with_the_default_gem_balance(app):
    """The balance is a column default, so a caller does not have to set it."""
    with app.app_context():
        user = User(username="fresh-user", email="fresh@example.com")
        user.set_password("correct-password")

        db.session.add(user)
        db.session.commit()

        assert db.session.get(User, user.id).gem_balance == DEFAULT_GEM_BALANCE
        assert DEFAULT_GEM_BALANCE == Decimal("500.00")
