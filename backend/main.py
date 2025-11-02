from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
import os
from datetime import datetime, timedelta
import stripe
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

# Payment routes
@app.route('/api/payments/create-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    try:
        data = request.get_json()
        amount = int(data.get('amount', 0) * 100)
        
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=data.get('currency', 'usd'),
            description=data.get('description', 'Art Gallery Purchase'),
            metadata={'user_id': get_jwt_identity()}
        )
        
        return jsonify({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Payment initialization failed'}), 500

@app.route('/api/payments/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # In production, verify the webhook signature
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"Payment succeeded: {payment_intent['id']}")
        
        # Update order status if needed
        user_id = payment_intent.get('metadata', {}).get('user_id')
        if user_id:
            # Find recent pending order for this user
            recent_order = Order.query.filter_by(
                customer_id=user_id, 
                status='pending'
            ).order_by(Order.created_at.desc()).first()
            
            if recent_order:
                recent_order.status = 'confirmed'
                db.session.commit()
                print(f"Order {recent_order.id} confirmed")
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"Payment failed: {payment_intent['id']}")
    
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