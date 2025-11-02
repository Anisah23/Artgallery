import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { WishlistContext } from '../context/WishlistContext';
import '../styles/components/ArtCard.css';

const ArtCard = ({ artwork }) => {
  const { addToWishlist, removeFromWishlist, isInWishlist } = useContext(WishlistContext);

  const handleWishlistClick = () => {
    if (isInWishlist(artwork.id)) {
      removeFromWishlist(artwork.id);
    } else {
      addToWishlist(artwork);
    }
  };

  return (
    <div className="art-card">
      <img src={artwork.image} alt={artwork.title} className="art-card-image" />
      <div className="art-card-content">
        <h3 className="art-card-title">{artwork.title}</h3>
        <p className="art-card-description">{artwork.description}</p>
        <p className="art-card-price">{artwork.price}</p>
        <button className="art-card-buy-button">Buy</button>
      </div>
      <button onClick={handleWishlistClick} className={`art-card-wishlist-button ${isInWishlist(artwork.id) ? 'active' : ''}`}>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="art-card-wishlist-icon">
          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
        </svg>
      </button>
    </div>
  );
};

ArtCard.propTypes = {
  artwork: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    price: PropTypes.string.isRequired,
    image: PropTypes.string.isRequired,
  }).isRequired,
};

export default ArtCard;