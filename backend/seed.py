#!/usr/bin/env python3
"""
Enhanced seed script with Faker for generating realistic test data
"""

import os
import sys
from datetime import datetime, timedelta
from faker import Faker
import random
from werkzeug.security import generate_password_hash

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.artwork import Artwork
from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.models.wishlist import WishlistItem

fake = Faker()

def create_base64_svg(text, color="#f3f4f6"):
    """Generate a base64 SVG image"""
    svg = f'''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{color}"/>
        <text x="50%" y="50%" font-family="Arial" font-size="16" fill="#9CA3AF" text-anchor="middle" dy=".3em">{text}</text>
    </svg>'''
    import base64
    return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"

def seed_users():
    """Create sample users"""
    print("Creating users...")
    
    # Create specific test users
    artist = User(
        username='artist1',
        email='artist@example.com',
        full_name='Sample Artist',
        role='artist',
        password_hash=generate_password_hash('password123')
    )
    
    collector = User(
        username='collector1', 
        email='collector@example.com',
        full_name='Sample Collector',
        role='collector',
        password_hash=generate_password_hash('password123')
    )
    
    db.session.add_all([artist, collector])
    
    # Create random artists
    artists = []
    for _ in range(8):
        artist = User(
            username=fake.user_name(),
            email=fake.email(),
            full_name=fake.name(),
            role='artist',
            password_hash=generate_password_hash('password123')
        )
        artists.append(artist)
        db.session.add(artist)
    
    # Create random collectors
    collectors = []
    for _ in range(15):
        collector = User(
            username=fake.user_name(),
            email=fake.email(), 
            full_name=fake.name(),
            role='collector',
            password_hash=generate_password_hash('password123')
        )
        collectors.append(collector)
        db.session.add(collector)
    
    db.session.commit()
    return artists + [artist], collectors + [collector]

def seed_artworks(artists):
    """Create sample artworks"""
    print("Creating artworks...")
    
    categories = ['painting', 'sculpture', 'photography', 'digital', 'mixed_media', 'drawing']
    art_styles = ['Abstract', 'Realistic', 'Modern', 'Contemporary', 'Minimalist', 'Expressionist']
    art_subjects = ['Landscape', 'Portrait', 'Still Life', 'Nature', 'Urban', 'Fantasy', 'Geometric']
    
    artworks = []
    for artist in artists:
        # Each artist creates 3-8 artworks
        num_artworks = random.randint(3, 8)
        
        for _ in range(num_artworks):
            style = random.choice(art_styles)
            subject = random.choice(art_subjects)
            
            artwork = Artwork(
                title=f"{style} {subject} {fake.word().title()}",
                description=fake.text(max_nb_chars=200),
                price=round(random.uniform(50, 2000), 2),
                category=random.choice(categories),
                image_url=create_base64_svg(f"{style} Art"),
                artist_id=artist.id,
                is_available=random.choice([True, True, True, False])  # 75% available
            )
            artworks.append(artwork)
            db.session.add(artwork)
    
    db.session.commit()
    return artworks

def seed_orders(collectors, artworks):
    """Create sample orders"""
    print("Creating orders...")
    
    statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered']
    
    for collector in collectors[:10]:  # Only some collectors have orders
        # Each collector has 1-4 orders
        num_orders = random.randint(1, 4)
        
        for _ in range(num_orders):
            order_date = fake.date_time_between(start_date='-6M', end_date='now')
            
            order = Order(
                customer_id=collector.id,
                total_amount=0,  # Will calculate from items
                status=random.choice(statuses),
                created_at=order_date,
                shipping_address=fake.street_address(),
                shipping_city=fake.city(),
                shipping_postal_code=fake.postcode(),
                shipping_country=fake.country()
            )
            
            # Note: tracking info would be in delivery table, not order table
            
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Add 1-3 items to each order
            total = 0
            num_items = random.randint(1, 3)
            selected_artworks = random.sample(artworks, min(num_items, len(artworks)))
            
            for artwork in selected_artworks:
                quantity = random.randint(1, 2)
                item_total = artwork.price * quantity
                total += item_total
                
                order_item = OrderItem(
                    order_id=order.id,
                    artwork_id=artwork.id,
                    quantity=quantity,
                    price=artwork.price
                )
                db.session.add(order_item)
            
            order.total_amount = total
    
    db.session.commit()

def seed_cart_items(collectors, artworks):
    """Create sample cart items"""
    print("Creating cart items...")
    
    from app.models.cart import Cart
    
    for collector in collectors[:5]:  # Only some collectors have cart items
        # Create cart for collector
        cart = Cart(user_id=collector.id)
        db.session.add(cart)
        db.session.flush()  # Get cart ID
        
        # Each collector has 1-4 items in cart
        num_items = random.randint(1, 4)
        selected_artworks = random.sample(artworks, min(num_items, len(artworks)))
        
        for artwork in selected_artworks:
            cart_item = CartItem(
                cart_id=cart.id,
                artwork_id=artwork.id,
                quantity=random.randint(1, 2)
            )
            db.session.add(cart_item)
    
    db.session.commit()

def seed_wishlist_items(collectors, artworks):
    """Create sample wishlist items"""
    print("Creating wishlist items...")
    
    from app.models.wishlist import Wishlist
    
    for collector in collectors[:8]:  # Most collectors have wishlist items
        # Create wishlist for collector
        wishlist = Wishlist(user_id=collector.id)
        db.session.add(wishlist)
        db.session.flush()  # Get wishlist ID
        
        # Each collector has 2-8 items in wishlist
        num_items = random.randint(2, 8)
        selected_artworks = random.sample(artworks, min(num_items, len(artworks)))
        
        for artwork in selected_artworks:
            wishlist_item = WishlistItem(
                wishlist_id=wishlist.id,
                artwork_id=artwork.id
            )
            db.session.add(wishlist_item)
    
    db.session.commit()

def main():
    """Main seeding function"""
    print("Starting database seeding with Faker...")
    
    app = create_app()
    with app.app_context():
        # Drop and recreate all tables
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating tables...")
        db.create_all()
        
        # Seed data
        artists, collectors = seed_users()
        artworks = seed_artworks(artists)
        seed_orders(collectors, artworks)
        seed_cart_items(collectors, artworks)
        seed_wishlist_items(collectors, artworks)
        
        print("Seeding complete!")
        print(f"   - {len(artists)} artists created")
        print(f"   - {len(collectors)} collectors created") 
        print(f"   - {len(artworks)} artworks created")
        print(f"   - Sample orders, cart items, and wishlist items created")
        print("\nTest accounts:")
        print(f"   Artist: artist@example.com / password123")
        print(f"   Collector: collector@example.com / password123")

if __name__ == '__main__':
    main()