from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.wishlist import Wishlist, WishlistItem, WishlistSchema
from ..models.artwork import Artwork
from ..utils.decorators import handle_api_errors
from ..utils.notification_service import NotificationService

wishlist_schema = WishlistSchema()

class WishlistResource(Resource):
    @jwt_required()
    @handle_api_errors
    def get(self):
        user_id = get_jwt_identity()
        wishlist = Wishlist.query.filter_by(user_id=user_id).first()
        
        if not wishlist:
            wishlist = Wishlist(user_id=user_id)
            db.session.add(wishlist)
            db.session.commit()
        
        return wishlist_schema.dump(wishlist), 200

    @jwt_required()
    @handle_api_errors
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        artwork_id = data.get('artworkId')

        if not artwork_id:
            return {"message": "artworkId is required"}, 400

        artwork = Artwork.query.filter_by(id=artwork_id, is_available=True).first()
        if not artwork:
            return {"message": "Artwork not found or unavailable"}, 404

        wishlist = Wishlist.query.filter_by(user_id=user_id).first()
        if not wishlist:
            wishlist = Wishlist(user_id=user_id)
            db.session.add(wishlist)
            db.session.flush()

        existing_item = WishlistItem.query.filter_by(
            wishlist_id=wishlist.id, 
            artwork_id=artwork_id
        ).first()

        if existing_item:
            return {"message": "Item already in wishlist"}, 400

        wishlist_item = WishlistItem(
            wishlist_id=wishlist.id,
            artwork_id=artwork_id
        )
        db.session.add(wishlist_item)
        
        # Notify artist that their artwork was wishlisted
        NotificationService.notify_artwork_added_to_wishlist(artwork_id, user_id)
        
        db.session.commit()
        return wishlist_schema.dump(wishlist), 201

class WishlistItemResource(Resource):
    @jwt_required()
    @handle_api_errors
    def delete(self, artwork_id):
        user_id = get_jwt_identity()
        
        wishlist = Wishlist.query.filter_by(user_id=user_id).first()
        if not wishlist:
            return {"message": "Wishlist not found"}, 404

        wishlist_item = WishlistItem.query.filter_by(
            wishlist_id=wishlist.id, 
            artwork_id=artwork_id
        ).first()

        if not wishlist_item:
            return {"message": "Item not found in wishlist"}, 404

        db.session.delete(wishlist_item)
        db.session.commit()

        return wishlist_schema.dump(wishlist), 200