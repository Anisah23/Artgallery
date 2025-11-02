from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.artwork import Artwork, ArtworkSchema
from app.models.user import User
from app.utils.decorators import handle_api_errors
import uuid

artwork_schema = ArtworkSchema()
artworks_schema = ArtworkSchema(many=True)

class ArtistArtworkResource(Resource):
    @jwt_required()
    @handle_api_errors
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'artist':
            return {'message': 'Access denied'}, 403
        
        artworks = Artwork.query.filter_by(artist_id=user_id).all()
        return {
            'items': artworks_schema.dump(artworks)
        }, 200

    @jwt_required()
    @handle_api_errors
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'artist':
            return {'message': 'Access denied'}, 403
        
        data = request.get_json()
        
        artwork = Artwork(
            title=data['title'],
            description=data['description'],
            price=data['price'],
            category=data['category'],
            image_url=data.get('image_url'),
            artist_id=user_id
        )
        
        db.session.add(artwork)
        db.session.commit()
        
        return artwork_schema.dump(artwork), 201

class ArtistArtworkDetailResource(Resource):
    @jwt_required()
    @handle_api_errors
    def get(self, artwork_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'artist':
            return {'message': 'Access denied'}, 403
        
        try:
            uuid.UUID(artwork_id)
        except ValueError:
            return {"message": "Invalid artwork ID format"}, 400
        
        artwork = Artwork.query.filter_by(id=artwork_id, artist_id=user_id).first()
        if not artwork:
            return {'message': 'Artwork not found'}, 404
        
        return artwork_schema.dump(artwork), 200

    @jwt_required()
    @handle_api_errors
    def put(self, artwork_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'artist':
            return {'message': 'Access denied'}, 403
        
        try:
            uuid.UUID(artwork_id)
        except ValueError:
            return {"message": "Invalid artwork ID format"}, 400
        
        artwork = Artwork.query.filter_by(id=artwork_id, artist_id=user_id).first()
        if not artwork:
            return {'message': 'Artwork not found'}, 404
        
        data = request.get_json()
        
        artwork.title = data.get('title', artwork.title)
        artwork.description = data.get('description', artwork.description)
        artwork.price = data.get('price', artwork.price)
        artwork.category = data.get('category', artwork.category)
        artwork.image_url = data.get('image_url', artwork.image_url)
        
        db.session.commit()
        
        return artwork_schema.dump(artwork), 200

    @jwt_required()
    @handle_api_errors
    def delete(self, artwork_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'artist':
            return {'message': 'Access denied'}, 403
        
        try:
            uuid.UUID(artwork_id)
        except ValueError:
            return {"message": "Invalid artwork ID format"}, 400
        
        artwork = Artwork.query.filter_by(id=artwork_id, artist_id=user_id).first()
        if not artwork:
            return {'message': 'Artwork not found'}, 404
        
        db.session.delete(artwork)
        db.session.commit()
        
        return {'message': 'Artwork deleted successfully'}, 200