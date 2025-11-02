import stripe
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.payment import Payment, PaymentSchema
from ..config import get_config

config = get_config()
stripe.api_key = config.STRIPE_SECRET_KEY

api = Namespace('payments', description='Payment operations')

payment_intent_model = api.model('PaymentIntent', {
    'amount': fields.Float(required=True, description='Payment amount'),
    'currency': fields.String(default='usd', description='Currency code'),
    'description': fields.String(description='Payment description')
})

@api.route('/create-intent')
class CreatePaymentIntent(Resource):
    @api.expect(payment_intent_model)
    def post(self):
        """Create a Stripe PaymentIntent"""
        try:
            data = request.get_json()
            amount = data.get('amount', 0)
            
            if amount <= 0:
                return {'error': 'Invalid amount'}, 400
            
            # Create PaymentIntent with Stripe
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=data.get('currency', 'usd'),
                description=data.get('description', 'Art Gallery Purchase'),
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
            
        except stripe.error.StripeError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Payment initialization failed'}, 500

@api.route('/confirm')
class ConfirmPayment(Resource):
    @jwt_required()
    def post(self):
        """Confirm payment and create payment record"""
        try:
            data = request.get_json()
            payment_intent_id = data.get('payment_intent_id')
            order_id = data.get('order_id')
            
            if not payment_intent_id or not order_id:
                return {'error': 'Missing required fields'}, 400
            
            # Retrieve PaymentIntent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                # Create payment record
                payment = Payment(
                    order_id=order_id,
                    amount=intent.amount / 100,  # Convert from cents
                    status='completed',
                    transaction_id=payment_intent_id
                )
                
                db.session.add(payment)
                db.session.commit()
                
                payment_schema = PaymentSchema()
                return payment_schema.dump(payment)
            else:
                return {'error': 'Payment not completed'}, 400
                
        except stripe.error.StripeError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Payment confirmation failed'}, 500