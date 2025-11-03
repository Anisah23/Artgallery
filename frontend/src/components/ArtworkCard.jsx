import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWishlist } from '../context/WishlistContext';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import ArtworkModal from './ArtworkModal';
import '../styles/components/ArtworkCard.css';

export default function ArtworkCard({ artwork }) {
  const { addToWishlist, removeFromWishlist, isInWishlist } = useWishlist();
  const { addToCart } = useCart();
  const { isLoggedIn, role } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const handleAddToWishlist = (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isLoggedIn) {
      navigate('/auth');
      return;
    }

    if (isInWishlist(artwork.id)) {
      removeFromWishlist(artwork.id);
    } else {
      addToWishlist(artwork);
    }
  };

  const handleBuy = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isLoggedIn) {
      navigate('/auth');
      return;
    }

    if (role !== 'Collector') {
      alert('Only collectors can purchase artworks');
      return;
    }

    setLoading(true);
    try {
      const result = await addToCart(artwork.id);
      if (result.success) {
        navigate('/cart');
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      alert('Error adding to cart. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCardClick = () => {
    setShowModal(true);
  };

  return (
    <>
      <div className="art-gallery-card" onClick={handleCardClick}>
        <div className="card-image-container">
          <img
            src={artwork.image_url || artwork.imageUrl}
            alt={artwork.title}
            className="card-image"
            onError={(e) => {
              e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzlDQTNBRiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIEltYWdlPC90ZXh0Pjwvc3ZnPg==';
            }}
          />
          {role === 'Collector' && (
            <button
              onClick={handleAddToWishlist}
              className={`wishlist-btn ${isInWishlist(artwork.id) ? 'active' : ''}`}
              title={isInWishlist(artwork.id) ? 'Remove from Wishlist' : 'Add to Wishlist'}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill={isInWishlist(artwork.id) ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
            </button>
          )}
          <div className="category-tag">{artwork.category}</div>
        </div>
        <div className="card-content">
          <h3 className="card-title">{artwork.title}</h3>
          <p className="card-description">{artwork.description}</p>
          <div className="card-footer">
            <p className="artwork-price">${artwork.price.toLocaleString()}</p>
            {role === 'Collector' && (
              <button
                className="buy-button"
                onClick={handleBuy}
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Buy'}
              </button>
            )}
          </div>
        </div>
      </div>
      
      <ArtworkModal 
        artwork={artwork}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
      />
    </>
  );
}
