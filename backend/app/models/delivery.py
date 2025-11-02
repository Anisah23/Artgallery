from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from ..extensions import db, ma

class Delivery(db.Model):
    __tablename__ = "deliveries"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey("orders.id"), nullable=False)
    status = db.Column(db.String(50), default="pending")
    tracking_number = db.Column(db.String(120))
    carrier = db.Column(db.String(80), default="standard")
    estimated_delivery = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DeliverySchema(ma.SQLAlchemyAutoSchema):
    created_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')
    updated_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = Delivery
        load_instance = True
        include_fk = True