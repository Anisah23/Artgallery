from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint
from ..extensions import db, ma


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default="pending", nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_country = db.Column(db.String(100), nullable=False)
    shipping_postal_code = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="order", lazy=True)
    deliveries = db.relationship("Delivery", backref="order", lazy=True)

    __table_args__ = (
        CheckConstraint(status.in_(['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'])),
    )


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey("orders.id"), nullable=False)
    artwork_id = db.Column(UUID(as_uuid=True), db.ForeignKey("artworks.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    artwork = db.relationship("Artwork")


class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    price = ma.Method("get_price")
    artwork = ma.Nested(lambda: ArtworkSchema(exclude=('artist',)), dump_only=True)

    def get_price(self, obj):
        return float(obj.price) if obj.price is not None else None

    class Meta:
        model = OrderItem
        load_instance = True
        include_fk = True


class OrderSchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(OrderItemSchema, many=True)
    payments = ma.Nested(lambda: PaymentSchema(many=True, exclude=('order',)), dump_only=True)
    deliveries = ma.Nested(lambda: DeliverySchema(many=True, exclude=('order',)), dump_only=True)
    created_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')
    updated_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')
    total_amount = ma.Method("get_total_amount")

    def get_total_amount(self, obj):
        return float(obj.total_amount) if obj.total_amount is not None else None

    class Meta:
        model = Order
        load_instance = True
        include_fk = True


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_item_schema = OrderItemSchema()