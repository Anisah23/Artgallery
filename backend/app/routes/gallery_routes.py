from flask import request
from flask_restful import Resource
from sqlalchemy import or_
from app.extensions import db
from app.models.artwork import Artwork, ArtworkSchema
from app.models.user import User
from app.utils.helpers import paginate_query
from app.utils.decorators import handle_api_errors
import uuid

artwork_schema = ArtworkSchema()
artworks_schema = ArtworkSchema(many=True)

class GalleryResource(Resource):
    @handle_api_errors
    def get(self, artwork_id=None):
        if artwork_id:
            return self.get_single_artwork(artwork_id)
        return self.get_artworks()

    def get_single_artwork(self, artwork_id):
        # Validate UUID format
        try:
            uuid.UUID(artwork_id)
        except ValueError:
            return {"message": "Invalid artwork ID format"}, 400
            
        artwork = Artwork.query.filter_by(id=artwork_id, is_available=True).first()
        if not artwork:
            return {"message": "Artwork not found"}, 404

        artist = User.query.filter_by(id=artwork.artist_id).first()
        artwork_data = artwork_schema.dump(artwork)
        artwork_data['artist'] = artist.username if artist else 'Unknown Artist'

        return artwork_data, 200

    def get_artworks(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        sort = request.args.get('sort', 'newest')
        min_price = request.args.get('minPrice', type=float)
        max_price = request.args.get('maxPrice', type=float)

        query = Artwork.query.filter_by(is_available=True)

        # Apply filters
        if category and category != 'All Categories':
            query = query.filter_by(category=category.lower())

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Artwork.title.ilike(search_term),
                    Artwork.description.ilike(search_term)
                )
            )

        if min_price is not None:
            query = query.filter(Artwork.price >= min_price)

        if max_price is not None:
            query = query.filter(Artwork.price <= max_price)

        # Apply sorting
        if sort == 'oldest':
            query = query.order_by(Artwork.created_at.asc())
        elif sort == 'price-low':
            query = query.order_by(Artwork.price.asc())
        elif sort == 'price-high':
            query = query.order_by(Artwork.price.desc())
        else:  # newest
            query = query.order_by(Artwork.created_at.desc())

        pagination = paginate_query(query, page, per_page)
        artworks = artworks_schema.dump(pagination.items)
        
        # Add artist names
        for artwork in artworks:
            artist = User.query.filter_by(id=artwork['artist_id']).first()
            artwork['artist'] = artist.username if artist else 'Unknown Artist'

        return {
            'items': artworks,
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }, 200