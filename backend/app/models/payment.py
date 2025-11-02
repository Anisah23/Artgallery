from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from ..extensions import db, ma

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey("orders.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    provider = db.Column(db.String(80), default="stripe")
    status = db.Column(db.String(50), default="pending")
    transaction_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PaymentSchema(ma.SQLAlchemyAutoSchema):
    created_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')
    updated_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')
    amount = ma.Method("get_amount")

    def get_amount(self, obj):
        return float(obj.amount) if obj.amount is not None else None

    class Meta:
        model = Payment
        load_instance = True
        include_fk = True