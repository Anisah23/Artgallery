# Routes package
from . import auth_routes
from . import gallery_routes
from . import artist_routes
from . import customer_routes
from . import order_routes
from . import cart_routes
from . import wishlist_routes

__all__ = [
    'auth_routes',
    'gallery_routes', 
    'artist_routes',
    'customer_routes',
    'order_routes',
    'cart_routes',
    'wishlist_routes'
]
