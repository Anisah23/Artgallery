from ..extensions import db
from ..models.notification import Notification
from ..models.user import User
from ..models.artwork import Artwork

class NotificationService:
    @staticmethod
    def create_notification(user_id, title, message, notification_type="info"):
        """Create a new notification for a user"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type
            )
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception as e:
            print(f"Error creating notification: {str(e)}")
            return None

    @staticmethod
    def notify_order_placed(order):
        """Notify artists when their artwork is ordered"""
        for item in order.items:
            artwork = item.artwork
            if artwork and artwork.artist_id:
                NotificationService.create_notification(
                    user_id=artwork.artist_id,
                    title="New Order Received",
                    message=f"Your artwork '{artwork.title}' has been ordered by a collector.",
                    notification_type="order"
                )

    @staticmethod
    def notify_order_status_change(order, new_status):
        """Notify collector when order status changes"""
        NotificationService.create_notification(
            user_id=order.customer_id,
            title="Order Status Updated",
            message=f"Your order #{str(order.id)[:8]} status has been updated to {new_status}.",
            notification_type="order"
        )

    @staticmethod
    def notify_artwork_added_to_cart(artwork_id, collector_id):
        """Notify artist when their artwork is added to cart"""
        artwork = Artwork.query.get(artwork_id)
        if artwork and artwork.artist_id:
            NotificationService.create_notification(
                user_id=artwork.artist_id,
                title="Artwork Added to Cart",
                message=f"A collector has added your artwork '{artwork.title}' to their cart.",
                notification_type="cart"
            )

    @staticmethod
    def notify_artwork_added_to_wishlist(artwork_id, collector_id):
        """Notify artist when their artwork is wishlisted"""
        artwork = Artwork.query.get(artwork_id)
        if artwork and artwork.artist_id:
            NotificationService.create_notification(
                user_id=artwork.artist_id,
                title="Artwork Wishlisted",
                message=f"A collector has added your artwork '{artwork.title}' to their wishlist.",
                notification_type="wishlist"
            )

    @staticmethod
    def notify_new_artwork_published(artist_id):
        """Notify when artist publishes new artwork"""
        NotificationService.create_notification(
            user_id=artist_id,
            title="Artwork Published",
            message="Your new artwork has been successfully published and is now visible to collectors.",
            notification_type="artwork"
        )

    @staticmethod
    def notify_payment_received(order):
        """Notify artists when payment is received for their artwork"""
        for item in order.items:
            artwork = item.artwork
            if artwork and artwork.artist_id:
                NotificationService.create_notification(
                    user_id=artwork.artist_id,
                    title="Payment Received",
                    message=f"Payment has been received for your artwork '{artwork.title}'.",
                    notification_type="payment"
                )

    @staticmethod
    def notify_welcome(user_id, user_role):
        """Send welcome notification to new users"""
        if user_role == 'artist':
            message = "Welcome to ArtMarket! Start uploading your artworks to reach collectors worldwide."
        else:
            message = "Welcome to ArtMarket! Discover amazing artworks from talented artists."
        
        NotificationService.create_notification(
            user_id=user_id,
            title="Welcome to ArtMarket!",
            message=message,
            notification_type="welcome"
        )