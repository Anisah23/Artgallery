import React, { useContext } from 'react';
import { WishlistContext } from '../context/WishlistContext';
import { Heart, ShoppingCart, X } from "lucide-react";
import { apiRequest } from '../utils/api';
import '../styles/pages/Wishlist.css';

const Wishlist = () => {
  const { wishlist, removeFromWishlist } = useContext(WishlistContext);

  const handlePurchase = async (art) => {
    try {
      // Add to cart instead of direct purchase
      await apiRequest('/api/cart/', {
        method: 'POST',
        body: JSON.stringify({ artworkId: art.id, quantity: 1 }),
      });
      console.log(`${art.title} added to cart!`);
    } catch (error) {
      console.error('Error adding to cart:', error);
      console.error('Failed to add to cart');
    }
  };

  return (
    <div className="wishlist-container">
      <div className="wishlist-content">
        <div className="wishlist-header">
          <h1 className="wishlist-title">My Wishlist</h1>
          <p className="wishlist-count">
            {wishlist.length}{" "}
            {wishlist.length === 1 ? "item" : "items"} in your wishlist
          </p>
        </div>

        {wishlist.length === 0 ? (
          <div className="wishlist-empty">
            <Heart className="empty-icon" size={64} />
            <p className="empty-text">Your wishlist is empty</p>
            <p className="empty-subtext">
              Browse the gallery and add artworks you love!
            </p>
          </div>
        ) : (
          <div className="wishlist-grid">
            {wishlist.map((art) => (
              <div key={art.id} className="wishlist-card">
                <div className="wishlist-image-container">
                  <img 
                    src={art.image_url || art.imageUrl} 
                    alt={art.title} 
                    className="wishlist-image"
                    onError={(e) => {
                      e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzlDQTNBRiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIEltYWdlPC90ZXh0Pjwvc3ZnPg==';
                    }}
                  />
                  <button
                    onClick={() => {
                      removeFromWishlist(art.id);
                      console.log("Removed from wishlist");
                    }}
                    className="wishlist-remove-btn"
                  >
                    <X size={20} className="remove-icon" />
                  </button>
                  <div className="wishlist-category-overlay">
                    <span className="wishlist-category">{art.category}</span>
                  </div>
                </div>

                <div className="wishlist-card-content">
                  <h3 className="art-title">{art.title}</h3>
                  <p className="art-description">{art.description}</p>
                  <p className="art-artisan">by {art.artist}</p>
                  <div className="wishlist-price-section">
                    <span className="art-price">${art.price}</span>
                  </div>
                  <button
                    className="wishlist-purchase-btn"
                    onClick={() => handlePurchase(art)}
                  >
                    <ShoppingCart size={16} className="purchase-icon" />
                    Purchase Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {wishlist.length > 0 && (
          <div className="wishlist-total-card">
            <div className="wishlist-total-content">
              <div>
                <p className="total-label">Total Wishlist Value</p>
                <p className="total-amount">
                  $
                  {wishlist
                    .reduce((sum, art) => sum + art.price, 0)
                    .toFixed(2)}
                </p>
              </div>
              <button
                className="wishlist-purchase-all-btn"
                onClick={async () => {
                  try {
                    for (const art of wishlist) {
                      await apiRequest('/api/cart/', {
                        method: 'POST',
                        body: JSON.stringify({ artworkId: art.id, quantity: 1 }),
                      });
                    }
                    console.log("All items added to cart!");
                  } catch (error) {
                    console.error('Error adding items to cart:', error);
                    console.log('Failed to add some items to cart');
                  }
                }}
              >
                <ShoppingCart className="purchase-icon" size={20} />
                Add All to Cart
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Wishlist;