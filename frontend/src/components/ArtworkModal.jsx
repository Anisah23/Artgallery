import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiRequest } from '../utils/api';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Separator } from "./ui/separator";
import { Heart, ShoppingCart, X, User, Tag, Calendar, DollarSign } from "lucide-react";
import { toast } from "sonner";
import '../styles/components/ArtworkModal.css';

export default function ArtworkModal({ artwork, isOpen, onClose }) {
  const { isLoggedIn, role } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAddToCart = async () => {
    if (!isLoggedIn) {
      toast.error('Please log in to add items to cart');
      return;
    }

    try {
      await apiRequest('/api/cart/', {
        method: 'POST',
        body: JSON.stringify({ artworkId: artwork.id }),
      });
      toast.success('Added to cart!');
      onClose();
    } catch (error) {
      console.error('Error adding to cart:', error);
      toast.error('Error adding to cart');
    }
  };

  const handleAddToWishlist = async () => {
    if (!isLoggedIn) {
      toast.error('Please log in to add items to wishlist');
      return;
    }

    try {
      await apiRequest('/api/wishlist/', {
        method: 'POST',
        body: JSON.stringify({ artworkId: artwork.id }),
      });
      toast.success('Added to wishlist!');
    } catch (error) {
      console.error('Error adding to wishlist:', error);
      toast.error('Error adding to wishlist');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="artwork-modal-overlay" onClick={onClose}>
      <div className="artwork-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={24} />
        </button>

        {loading && (
          <div className="modal-loading">Loading artwork...</div>
        )}

        {error && (
          <div className="modal-error">{error}</div>
        )}

        {artwork && (
          <div className="modal-content">
            <div className="modal-image">
              <img
                src={artwork.image_url}
                alt={artwork.title}
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzlDQTNBRiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIEltYWdlPC90ZXh0Pjwvc3ZnPg==';
                }}
              />
            </div>

            <div className="modal-info">
              <div className="modal-header">
                <h2 className="modal-title">{artwork.title}</h2>
                <div className="modal-meta">
                  <div className="meta-item">
                    <User size={16} />
                    <span>by {artwork.artist}</span>
                  </div>
                  <div className="meta-item">
                    <Tag size={16} />
                    <span>{artwork.category}</span>
                  </div>
                  <div className="meta-item">
                    <Calendar size={16} />
                    <span>{new Date(artwork.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              <div className="modal-price">
                <DollarSign size={20} />
                <span>${artwork.price}</span>
              </div>

              <Separator className="my-4" />

              <div className="modal-description">
                <h3>Description</h3>
                <p>{artwork.description}</p>
              </div>

              <Separator className="my-4" />

              <div className="modal-actions">
                {role === 'collector' && (
                  <div className="action-buttons">
                    <Button onClick={handleAddToCart} className="add-to-cart-btn">
                      <ShoppingCart size={18} />
                      Add to Cart
                    </Button>
                    <Button variant="outline" onClick={handleAddToWishlist}>
                      <Heart size={18} />
                      Add to Wishlist
                    </Button>
                  </div>
                )}
                {role === 'artist' && (
                  <div className="artist-view">
                    <p className="artist-note">Viewing as artist - Purchase options not available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}