import React, { createContext, useState, useEffect, useContext } from 'react';
import { useAuth } from './AuthContext';
import { apiRequest } from '../utils/api';

export const WishlistContext = createContext();

export const WishlistProvider = ({ children }) => {
  const [wishlist, setWishlist] = useState([]);
  const [loading, setLoading] = useState(false);
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    if (isLoggedIn) {
      fetchWishlist();
    } else {
      // Load from localStorage for non-logged-in users
      const savedWishlist = JSON.parse(localStorage.getItem('wishlist')) || [];
      setWishlist(savedWishlist);
    }
  }, [isLoggedIn]);

  const fetchWishlist = async () => {
    try {
      setLoading(true);
      if (isLoggedIn) {
        const data = await apiRequest('/api/wishlist/');
        // Handle structured response - extract artwork data from items
        const items = data.items || data || [];
        const artworks = items.map(item => item.artwork || item).filter(Boolean);
        setWishlist(artworks);
      } else {
        const savedWishlist = JSON.parse(localStorage.getItem('wishlist')) || [];
        setWishlist(savedWishlist);
      }
    } catch (error) {
      console.error('Error fetching wishlist:', error);
      // Fall back to localStorage
      const savedWishlist = JSON.parse(localStorage.getItem('wishlist')) || [];
      setWishlist(savedWishlist);
    } finally {
      setLoading(false);
    }
  };

  const addToWishlist = async (artwork) => {
    if (isLoggedIn) {
      try {
        const data = await apiRequest('/api/wishlist/', {
          method: 'POST',
          body: JSON.stringify({ artworkId: artwork.id }),
        });
        const items = data.items || data || [];
        const artworks = items.map(item => item.artwork || item).filter(Boolean);
        setWishlist(artworks);
        return;
      } catch (error) {
        console.error('Error adding to backend wishlist:', error);
        // Fall back to localStorage
      }
    }

    // Update local state and localStorage for non-logged-in users or fallback
    const newWishlist = [...wishlist, artwork];
    setWishlist(newWishlist);
    localStorage.setItem('wishlist', JSON.stringify(newWishlist));
  };

  const removeFromWishlist = async (artworkId) => {
    if (isLoggedIn) {
      try {
        const data = await apiRequest(`/api/wishlist/${artworkId}`, {
          method: 'DELETE',
        });
        const items = data.items || data || [];
        const artworks = items.map(item => item.artwork || item).filter(Boolean);
        setWishlist(artworks);
        return;
      } catch (error) {
        console.error('Error removing from backend wishlist:', error);
        // Fall back to localStorage
      }
    }

    // Update local state and localStorage for non-logged-in users or fallback
    const newWishlist = wishlist.filter((item) => item.id !== artworkId);
    setWishlist(newWishlist);
    localStorage.setItem('wishlist', JSON.stringify(newWishlist));
  };

  const isInWishlist = (artworkId) => {
    return wishlist.some((item) => item.id === artworkId);
  };

  const wishlistCount = wishlist.length;

  return (
    <WishlistContext.Provider value={{
      wishlist,
      loading,
      addToWishlist,
      removeFromWishlist,
      isInWishlist,
      wishlistCount,
      fetchWishlist
    }}>
      {children}
    </WishlistContext.Provider>
  );
};

export const useWishlist = () => {
  const context = useContext(WishlistContext);
  if (!context) {
    throw new Error('useWishlist must be used within a WishlistProvider');
  }
  return context;
};
