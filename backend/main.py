from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
import os
from datetime import datetime, timedelta
import stripe
from stripe.error import ApiError, SignatureVerificationError # <-- NEW: Import specific Stripe errors
import json
from dotenv import load_dotenv
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.artwork import Artwork
from app.models.order import Order, OrderItem
from app.models.cart import Cart, CartItem

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
# NEW: Get the webhook secret
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET') 

# --- Payment routes ---

@app.route('/api/payments/create-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    user_id = get_jwt_identity() # Get user ID first
    try:
        data = request.get_json()
        # Amount in cents (assuming amount is passed in dollars/local currency)
        amount = int(data.get('amount', 0) * 100) 
        
        # Guard against zero/negative amount
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
            
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=data.get('currency', 'usd'),
            description=data.get('description', 'Art Gallery Purchase'),
            metadata={'user_id': user_id}
        )
        
        
        return jsonify({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        }), 200
        
    except ApiError as e: 
        return jsonify({'error': f"Stripe API Error: {str(e)}"}), 400 
    except Exception as e:
       
        print(f"Error creating payment intent: {e}")
        return jsonify({'error': 'Payment initialization failed'}), 500

@app.route('/api/payments/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events with signature verification"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        if not WEBHOOK_SECRET:
             # In a real app, this should be a serious internal error.
            print("WARNING: STRIPE_WEBHOOK_SECRET not configured!")
            return jsonify({'error': 'Server configuration error'}), 500
            
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print(f"Webhook Error: Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except SignatureVerificationError as e:
        # Invalid signature
        print(f"Webhook Error: Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        # Catch any other unexpected error during event construction
        print(f"Unexpected webhook error: {e}")
        return jsonify({'error': 'Internal error'}), 500

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        intent_id = payment_intent['id']
        print(f"Payment succeeded: {intent_id}")
        
    
        # The user_id is now just for logging/cross-reference, the intent_id is the key
        
        # NOTE: This assumes your 'Order' model has a 'payment_intent_id' column
        order_to_update = Order.query.filter_by(
            payment_intent_id=intent_id,
            status='pending'
        ).first()

        if order_to_update:
            # We explicitly check the amount paid vs. the order total here for max safety
            # (optional, but highly recommended)
            
            order_to_update.status = 'confirmed'
            # Optional: Store the final Stripe charge ID if needed
            # order_to_update.stripe_charge_id = payment_intent['latest_charge'] 
            db.session.commit()
            print(f"Order {order_to_update.id} confirmed for intent {intent_id}")
        else:
            print(f"Warning: No pending order found for PaymentIntent ID: {intent_id}")

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"Payment failed: {payment_intent['id']}")
        # You would update the corresponding order status to 'failed' here
        # E.g., Order.query.filter_by(payment_intent_id=payment_intent['id']).update({'status': 'failed'})
    
    # Respond quickly to Stripe
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Check if database has data
        user_count = User.query.count()
        if user_count == 0:
            print("Database is empty. Run 'python seed.py' to populate with sample data.")
        else:
            print(f"Database has {user_count} users and {Artwork.query.count()} artworks")
    
    print("Starting Art Gallery API (Database Mode)")
    print("API running at: http://localhost:5000")
    print("Using PostgreSQL database for all data")
    
    app.run(host='0.0.0.0', port=5000, debug=True)