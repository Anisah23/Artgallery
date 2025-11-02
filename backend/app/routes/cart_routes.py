from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from ..extensions import db
from ..models.cart import Cart, CartItem, CartSchema
from ..models.artwork import Artwork
from ..models.user import User
from ..utils.decorators import handle_api_errors
from ..utils.notification_service import NotificationService

cart_schema = CartSchema()

class CartResource(Resource):
    @jwt_required()
    @handle_api_errors
    def get(self):
        user_id = get_jwt_identity()
        cart = Cart.query.filter_by(user_id=user_id).first()
        
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()
        
        return cart_schema.dump(cart), 200

    @jwt_required()
    @handle_api_errors
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        
        artwork_id = data.get('artworkId')
        quantity = data.get('quantity', 1)
        
        if not artwork_id:
            return {"message": "artworkId is required"}, 400
        
        # Verify artwork exists and is available
        artwork = Artwork.query.filter_by(id=artwork_id, is_available=True).first()
        if not artwork:
            return {"message": "Artwork not found or unavailable"}, 404
        
        # Get or create cart
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.flush()
        
        # Check if item already in cart
        cart_item = CartItem.query.filter_by(cart_id=cart.id, artwork_id=artwork_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, artwork_id=artwork_id, quantity=quantity)
            db.session.add(cart_item)
            # Notify artist that their artwork was added to cart
            NotificationService.notify_artwork_added_to_cart(artwork_id, user_id)
        
        db.session.commit()
        return cart_schema.dump(cart), 201

class CartItemResource(Resource):
    @jwt_required()
    @handle_api_errors
    def patch(self, artwork_id):
        user_id = get_jwt_identity()
        data = request.get_json()
        quantity = data.get('quantity')
        
        if quantity is None or quantity < 0:
            return {"message": "Valid quantity is required"}, 400
        
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            return {"message": "Cart not found"}, 404
        
        cart_item = CartItem.query.filter_by(cart_id=cart.id, artwork_id=artwork_id).first()
        if not cart_item:
            return {"message": "Item not found in cart"}, 404
        
        if quantity == 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = quantity
        
        db.session.commit()
        return cart_schema.dump(cart), 200

    @jwt_required()
    @handle_api_errors
    def delete(self, artwork_id):
        user_id = get_jwt_identity()
        
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            return {"message": "Cart not found"}, 404
        
        cart_item = CartItem.query.filter_by(cart_id=cart.id, artwork_id=artwork_id).first()
        if not cart_item:
            return {"message": "Item not found in cart"}, 404
        
        db.session.delete(cart_item)
        db.session.commit()
        return cart_schema.dump(cart), 200