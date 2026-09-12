"""Order database model."""

from app.extensions import db
from app.utils.serialization import iso_utc


class Order(db.Model):
    """A completed purchase of one product, at the price charged at the time."""

    __tablename__ = "orders"
    __table_args__ = (
        db.CheckConstraint("total_price >= 0", name="ck_orders_total_price_non_negative"),
        db.CheckConstraint(
            "gem_balance_after >= 0", name="ck_orders_gem_balance_after_non_negative"
        ),
        db.UniqueConstraint("user_id", "product_id", name="uq_orders_user_product"),
    )

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False, index=True
    )

    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    gem_balance_after = db.Column(db.Numeric(10, 2), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    user = db.relationship("User", back_populates="orders")
    
    product = db.relationship("Product", back_populates="orders")

    def to_dict(self) -> dict:
        """Return the order as the receipt the API exposes.

        The product is nested so a receipt page can be rendered from a single
        request.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_price": str(self.total_price),
            "gem_balance_before": str(self.gem_balance_after + self.total_price),
            "gem_balance_after": str(self.gem_balance_after),
            "created_at": iso_utc(self.created_at),
            "product": self.product.to_dict(),
        }
