from flask_restx import Api, Resource, fields
from flask import Blueprint, request
from flask_cors import CORS

# Create blueprint for Swagger
swagger_bp = Blueprint('swagger', __name__)
CORS(swagger_bp, supports_credentials=True)

# Initialize Flask-RESTX API
api = Api(
    swagger_bp,
    version='1.0',
    title='ArtMarket API',
    description='A comprehensive REST API for the ArtMarket digital art platform',
    doc='/docs/',
    security='Bearer Auth',
    authorizations={
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    }
)

# Namespaces
auth_ns = api.namespace('auth', description='Authentication operations')
gallery_ns = api.namespace('gallery', description='Gallery operations')
artist_ns = api.namespace('artist', description='Artist-specific operations')
collectors_ns = api.namespace('collectors', description='Collector-specific operations')
orders_ns = api.namespace('orders', description='Order management operations')
cart_ns = api.namespace('cart', description='Cart operations')
wishlist_ns = api.namespace('wishlist', description='Wishlist operations')
payments_ns = api.namespace('payments', description='Payment processing operations')

# Models
artwork_model = api.model('Artwork', {
    'id': fields.String(description='Artwork UUID'),
    'title': fields.String(required=True, description='Artwork title'),
    'description': fields.String(required=True, description='Artwork description'),
    'price': fields.Float(required=True, description='Artwork price'),
    'category': fields.String(required=True, description='Artwork category'),
    'image_url': fields.String(description='Artwork image URL'),
    'artist_id': fields.String(description='Artist UUID'),
    'artist': fields.String(description='Artist name'),
    'is_available': fields.Boolean(description='Artwork availability status'),
    'created_at': fields.String(description='Creation timestamp'),
})

# Import routes
from .routes import auth_routes, gallery_routes, artist_routes, customer_routes, order_routes, cart_routes, wishlist_routes

# Auth routes
@auth_ns.route('/login')
class LoginResource(Resource):
    def post(self):
        return auth_routes.LoginResource().post()

@auth_ns.route('/register')
class RegisterResource(Resource):
    def post(self):
        return auth_routes.RegisterResource().post()

# Gallery routes
@gallery_ns.route('/')
class GalleryListResource(Resource):
    def get(self):
        return gallery_routes.GalleryResource().get()
    
    def options(self):
        return {}, 200

@gallery_ns.route('/<string:artwork_id>')
class GalleryDetailResource(Resource):
    def get(self, artwork_id):
        return gallery_routes.GalleryResource().get(artwork_id)
    
    def options(self, artwork_id):
        return {}, 200

# Artist routes
@artist_ns.route('/artworks')
class ArtistArtworkResource(Resource):
    def get(self):
        return artist_routes.ArtistArtworkResource().get()
    
    def post(self):
        return artist_routes.ArtistArtworkResource().post()
    
    def options(self):
        return {}, 200

@artist_ns.route('/artworks/<string:artwork_id>')
class ArtistArtworkDetailResource(Resource):
    def get(self, artwork_id):
        return artist_routes.ArtistArtworkDetailResource().get(artwork_id)
    
    def put(self, artwork_id):
        return artist_routes.ArtistArtworkDetailResource().put(artwork_id)
    
    def delete(self, artwork_id):
        return artist_routes.ArtistArtworkDetailResource().delete(artwork_id)
    
    def options(self, artwork_id):
        return {}, 200

@artist_ns.route('/upload-image')
class UploadImageResource(Resource):
    def post(self):
        from flask import request
        from flask_jwt_extended import get_jwt_identity
        from app.models.user import User
        from app.utils.cloudinary_service import CloudinaryService
        
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role != 'artist':
                return {'message': 'Access denied'}, 403
        except:
            return {'message': 'Authentication required'}, 401
            
        if 'file' not in request.files:
            return {'message': 'No file provided'}, 400

        file = request.files['file']
        if file.filename == '':
            return {'message': 'No file selected'}, 400

        try:
            upload_result = CloudinaryService.upload_image(file)
            return {
                'image_url': upload_result['url'],
                'public_id': upload_result['public_id'],
                'message': 'Image uploaded successfully'
            }, 200
        except Exception as e:
            return {'message': f'Image upload failed: {str(e)}'}, 500
    
    def options(self):
        return {}, 200

# Cart routes
@cart_ns.route('/')
class CartResource(Resource):
    def get(self):
        return cart_routes.CartResource().get()
    
    def post(self):
        return cart_routes.CartResource().post()
    
    def options(self):
        return {}, 200

@cart_ns.route('/<string:artwork_id>')
class CartItemResource(Resource):
    def patch(self, artwork_id):
        return cart_routes.CartItemResource().patch(artwork_id)
    
    def delete(self, artwork_id):
        return cart_routes.CartItemResource().delete(artwork_id)
    
    def options(self, artwork_id):
        return {}, 200

# Wishlist routes
@wishlist_ns.route('/')
class WishlistResource(Resource):
    def get(self):
        return wishlist_routes.WishlistResource().get()
    
    def post(self):
        return wishlist_routes.WishlistResource().post()
    
    def options(self):
        return {}, 200

@wishlist_ns.route('/<string:artwork_id>')
class WishlistItemResource(Resource):
    def delete(self, artwork_id):
        return wishlist_routes.WishlistItemResource().delete(artwork_id)
    
    def options(self, artwork_id):
        return {}, 200

# Orders routes
@orders_ns.route('/')
class OrdersResource(Resource):
    def get(self):
        return order_routes.OrdersResource().get()
    
    def post(self):
        return order_routes.OrdersResource().post()
    
    def options(self):
        return {}, 200

# Collectors routes
@collectors_ns.route('/notifications')
class CollectorNotificationsResource(Resource):
    def get(self):
        try:
            from flask_jwt_extended import get_jwt_identity
            from app.models.notification import Notification
            
            user_id = get_jwt_identity()
            notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
            return [{
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.type,
                'read': n.read,
                'timestamp': n.created_at.isoformat() if n.created_at else None
            } for n in notifications], 200
        except Exception as e:
            return [], 200
    
    def options(self):
        return {}, 200



@payments_ns.route('/create-intent')
class PaymentIntentResource(Resource):
    def post(self):
        from flask_jwt_extended import get_jwt_identity
        import stripe
        import os
        
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            amount = int(data.get('amount', 0) * 100)  # Convert to cents
            
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_51SNtuKJxmqf3ZKkyhGZ5XbUVoMAquzLNUUWuSKfADC7XZMRsqLCtkkTblCKM9gkEodq9RliCNEaT5XvjrFfZO6IO00LTsLb4VF')
            
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=data.get('currency', 'usd'),
                description=data.get('description', 'Art Gallery Purchase'),
                metadata={'user_id': user_id}
            )
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }, 200
            
        except Exception as e:
            return {'error': 'Payment initialization failed'}, 500
    
    def options(self):
        return {}, 200