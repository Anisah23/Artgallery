from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import stripe
import os
from dotenv import load_dotenv
from ..extensions import db

# Load environment variables
load_dotenv()

# Initialize Stripe with environment variable directly
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
print(f'Stripe API key configured: {"Yes" if stripe.api_key else "No"}')
if stripe.api_key:
    print(f'Stripe key starts with: {stripe.api_key[:7]}...')
from ..models.order import Order, OrderSchema, OrderItem
from ..models.artwork import Artwork
from ..models.payment import Payment, PaymentSchema
from ..models.delivery import Delivery, DeliverySchema
from ..models.notification import Notification, NotificationSchema
from ..models.user import User
from ..utils.decorators import handle_api_errors
from ..utils.helpers import paginate_query
from ..utils.email_service import EmailService
from ..utils.notification_service import NotificationService

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
payment_schema = PaymentSchema()
delivery_schema = DeliverySchema()
notification_schema = NotificationSchema()

class OrdersResource(Resource):
    @jwt_required()
    @handle_api_errors
    def get(self):
        """Get orders based on user role"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if user.role == 'artist':
            # Artists see orders for their artworks
            query = Order.query.\
                join(OrderItem).\
                join(Artwork).\
                filter(Artwork.artist_id == user_id).\
                order_by(Order.created_at.desc())
        else:
            # Collectors see their own orders
            query = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc())

        pagination = paginate_query(query, page, per_page)

        return {
            'items': orders_schema.dump(pagination.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'total_pages': pagination.pages
            }
        }, 200

    @jwt_required()
    @handle_api_errors
    def post(self):
        """Create new order"""
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        if not data.get('items') or not isinstance(data['items'], list):
            return {'message': 'Order items are required'}, 400

        # Validate shipping details
        shipping_required = ['fullName', 'address', 'city', 'country', 'postalCode']
        shipping_details = data.get('shipping_details', {})
        for field in shipping_required:
            if not shipping_details.get(field):
                return {'message': f'Shipping {field} is required'}, 400

        # Calculate total and validate artworks
        total_amount = 0
        order_items = []

        for item in data['items']:
            artwork_id = item.get('artwork_id')
            quantity = item.get('quantity', 1)

            artwork = Artwork.query.filter_by(id=artwork_id, is_available=True).first()
            if not artwork:
                return {'message': f'Artwork {artwork_id} not found or unavailable'}, 404

            item_total = artwork.price * quantity
            total_amount += item_total

            order_item = OrderItem(
                artwork_id=artwork_id,
                quantity=quantity,
                price=item_total
            )
            order_items.append(order_item)

        # Create order
        order = Order(
            customer_id=user_id,
            total_amount=total_amount,
            shipping_address=shipping_details['address'],
            shipping_city=shipping_details['city'],
            shipping_country=shipping_details['country'],
            shipping_postal_code=shipping_details['postalCode'],
            items=order_items
        )

        db.session.add(order)
        db.session.commit()

        # Send notifications to artists
        NotificationService.notify_order_placed(order)
        NotificationService.notify_payment_received(order)

        # Send order confirmation email
        try:
            customer = User.query.get(user_id)
            if customer and customer.email:
                EmailService.send_order_confirmation(customer.email, order)
        except Exception as e:
            # Log error but don't fail the order creation
            import logging
            logging.error(f'Failed to send order confirmation email: {str(e)}')

        return order_schema.dump(order), 201

class OrderDetailResource(Resource):
    @jwt_required()
    @handle_api_errors
    def get(self, order_id):
        """Get specific order details"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        order = Order.query.get(order_id)
        if not order:
            return {'message': 'Order not found'}, 404

        # Check permissions
        if user.role == 'collector' and order.customer_id != user_id:
            return {'message': 'Access denied'}, 403

        if user.role == 'artist':
            # Check if artist has artworks in this order
            has_artwork = any(item.artwork.artist_id == user_id for item in order.items)
            if not has_artwork:
                return {'message': 'Access denied'}, 403

        return order_schema.dump(order), 200

    @jwt_required()
    @handle_api_errors
    def put(self, order_id):
        """Update order status"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        order = Order.query.get(order_id)
        if not order:
            return {'message': 'Order not found'}, 404

        # Check permissions
        if user.role == 'artist':
            has_artwork = any(item.artwork.artist_id == user_id for item in order.items)
            if not has_artwork:
                return {'message': 'Access denied'}, 403
        elif user.role == 'collector' and order.customer_id != user_id:
            return {'message': 'Access denied'}, 403

        data = request.get_json()
        new_status = data.get('status')

        if new_status and new_status in ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']:
            order.status = new_status
            db.session.commit()

            # Notify customer of status change
            NotificationService.notify_order_status_change(order, new_status)

        return order_schema.dump(order), 200

class StripePaymentIntentResource(Resource):
    @jwt_required()
    @handle_api_errors
    def post(self):
        """Create Stripe payment intent"""
        data = request.get_json()
        amount = data.get('amount')
        currency = data.get('currency', 'usd')

        if not amount or amount <= 0:
            return {'message': 'Valid amount is required'}, 400

        # Check if Stripe is configured
        if not stripe.api_key:
            print('Stripe API key is None or empty')
            return {'message': 'Stripe not configured'}, 500

        try:
            # Convert to cents for Stripe
            amount_cents = int(float(amount) * 100)

            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                automatic_payment_methods={'enabled': True},
                metadata={'integration_check': 'accept_a_payment'}
            )

            return {
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id
            }, 200

        except stripe.error.StripeError as e:
            print(f'Stripe error: {str(e)}')
            return {'message': f'Stripe error: {str(e)}'}, 400
        except Exception as e:
            print(f'Payment processing error: {str(e)}')
            return {'message': f'Payment processing error: {str(e)}'}, 500

class StripeWebhookResource(Resource):
    @handle_api_errors
    def post(self):
        """Handle Stripe webhooks"""
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
            )
        except ValueError as e:
            return {'message': 'Invalid payload'}, 400
        except stripe.error.SignatureVerificationError as e:
            return {'message': 'Invalid signature'}, 400

        # Handle payment intent succeeded
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Update order status or trigger other actions
            print(f'Payment succeeded: {payment_intent.id}')

        return {'status': 'success'}, 200