from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import UUID
import uuid
from marshmallow import fields
from ..extensions import db, ma


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="collector", nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    artworks = db.relationship("Artwork", backref="artist", lazy=True)

    # --- Password methods ---
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


# --- Marshmallow Schema ---
class UserSchema(ma.SQLAlchemyAutoSchema):
    # Convert UUID → string so Marshmallow doesn't break
    id = fields.Method("get_id")
    created_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')
    updated_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)

    def get_id(self, obj):
        """Ensure UUID is serialized as string"""
        return str(obj.id)


# --- Schema instances ---
user_schema = UserSchema()
users_schema = UserSchema(many=True)
