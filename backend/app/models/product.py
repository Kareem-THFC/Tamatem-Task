"""Product database model."""

from app.extensions import db
from app.utils.serialization import iso_utc


class Product(db.Model):
    """A purchasable item imported from the supplied CSV file."""

    __tablename__ = "products"
    __table_args__ = (
        db.CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    location = db.Column(db.String(10), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    orders = db.relationship("Order", back_populates="product")

    def to_dict(self) -> dict:
        """Return the product in the shape the API exposes.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": str(self.price),
            "location": self.location,
            "created_at": iso_utc(self.created_at),
        }
