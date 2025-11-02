from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from ..extensions import db, ma

class Wishlist(db.Model):
    __tablename__ = "wishlists"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship("WishlistItem", backref="wishlist", lazy=True, cascade="all, delete-orphan")

class WishlistItem(db.Model):
    __tablename__ = "wishlist_items"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wishlist_id = db.Column(UUID(as_uuid=True), db.ForeignKey("wishlists.id"), nullable=False)
    artwork_id = db.Column(UUID(as_uuid=True), db.ForeignKey("artworks.id"), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    artwork = db.relationship("Artwork")

class WishlistItemSchema(ma.SQLAlchemyAutoSchema):
    artwork = ma.Method('get_artwork_data', dump_only=True)
    
    def get_artwork_data(self, obj):
        if obj.artwork:
            return {
                'id': str(obj.artwork.id),
                'title': obj.artwork.title,
                'price': float(obj.artwork.price) if obj.artwork.price else 0,
                'image_url': obj.artwork.image_url,
                'category': obj.artwork.category,
                'description': obj.artwork.description,
                'artist': obj.artwork.artist.full_name if obj.artwork.artist else 'Unknown Artist'
            }
        return None

    class Meta:
        model = WishlistItem
        load_instance = True
        include_fk = True

class WishlistSchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(WishlistItemSchema, many=True)
    created_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')
    updated_at = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = Wishlist
        load_instance = True
        include_fk = True