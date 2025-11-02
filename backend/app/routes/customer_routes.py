from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.artwork import Artwork, ArtworkSchema
from ..models.order import Order
from ..models.user import User
from ..models.notification import Notification, NotificationSchema
from ..utils.decorators import role_required, handle_api_errors
from ..utils.helpers import paginate_query

artwork_schema = ArtworkSchema()
artworks_schema = ArtworkSchema(many=True)
notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)

class CustomerArtworksResource(Resource):
    
    @role_required(['collector'])
    @handle_api_errors
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)

        query = Artwork.query.filter_by(is_available=True).order_by(Artwork.created_at.desc())
        pagination = paginate_query(query, page, per_page)

        artworks = artworks_schema.dump(pagination.items)
        
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

class CustomerStatsResource(Resource):
    @role_required(['collector'])
    @handle_api_errors
    def get(self):
        user_id = get_jwt_identity()

        total_orders = Order.query.filter_by(customer_id=user_id).count()
        
        total_spent = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.customer_id == user_id,
            Order.status == 'delivered'
        ).scalar() or 0

        return {
            'total_orders': total_orders,
            'total_spent': float(total_spent)
        }, 200


class CustomerNotificationsResource(Resource):
    @role_required(['collector'])
    @handle_api_errors
    def get(self):
        user_id = get_jwt_identity()
        try:
            notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
            return notifications_schema.dump(notifications), 200
        except Exception as e:
            # Return empty list if table doesn't exist or other error
            print(f"Notification query error: {str(e)}")
            return [], 200

    @role_required(['collector'])
    @handle_api_errors
    def patch(self, notification_id):
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if not notification:
            return {"message": "Notification not found"}, 404

        data = request.get_json() or {}
        if 'read' in data:
            notification.read = data['read']
        db.session.commit()
        return notification_schema.dump(notification), 200

    @role_required(['collector'])
    @handle_api_errors
    def delete(self, notification_id):
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if not notification:
            return {"message": "Notification not found"}, 404

        db.session.delete(notification)
        db.session.commit()
        return {"message": "Notification deleted"}, 200