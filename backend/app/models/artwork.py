from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import validates, ValidationError, EXCLUDE
from ..extensions import db, ma


class Artwork(db.Model):
    __tablename__ = "artworks"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(1024))
    image_public_id = db.Column(db.String(255))  # Cloudinary public ID
    artist_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ArtworkSchema(ma.SQLAlchemyAutoSchema):
    created_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')
    updated_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')
    price = ma.Method("get_price")
    artist = ma.String(dump_only=True)  # Allow artist field for serialization

    @validates('price')
    def validate_price(self, value):
        if value <= 0:
            raise ValidationError('Price must be greater than 0')

    @validates('category')
    def validate_category(self, value):
        valid_categories = ['painting', 'sculpture', 'photography', 'digital', 'mixed-media', 'textile']
        if value.lower() not in valid_categories:
            raise ValidationError(f'Category must be one of: {", ".join(valid_categories)}')

    def get_price(self, obj):
        return float(obj.price) if obj.price is not None else None

    class Meta:
        model = Artwork
        load_instance = True
        include_fk = True
        unknown = EXCLUDE  # Ignore unknown fields


artwork_schema = ArtworkSchema()
artworks_schema = ArtworkSchema(many=True)