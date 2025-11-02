from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from ..extensions import db, ma

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    type = db.Column(db.String(50), default="info")
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NotificationSchema(ma.SQLAlchemyAutoSchema):
    created_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = Notification
        load_instance = True
        include_fk = True