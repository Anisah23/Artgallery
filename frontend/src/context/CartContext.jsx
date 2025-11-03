import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { apiRequest } from '../utils/api';
import { toast } from 'sonner';

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    if (isLoggedIn) {
      fetchCart();
    } else {
      setCart(null);
    }
  }, [isLoggedIn]);

  const fetchCart = async () => {
    try {
      setLoading(true);
      // Try to get from localStorage first
      const localCart = JSON.parse(localStorage.getItem('cart') || '{"items": []}');
      setCart(localCart);
    } catch (error) {
      console.error('Error fetching cart:', error);
      setCart({ items: [] });
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (artworkId, quantity = 1) => {
    try {
      // For now, use local storage since we're using test data
      const currentCart = JSON.parse(localStorage.getItem('cart') || '{"items": []}');
      const existingItem = currentCart.items.find(item => item.artwork_id === artworkId);
      
      if (existingItem) {
        existingItem.quantity += quantity;
      } else {
        // Find artwork from test data
        const testArtworks = [
          { id: 1, title: "Starry Night Dreams", description: "Abstract interpretation of Van Gogh's masterpiece", price: 450.00, category: "painting", image_url: "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=400&h=300&fit=crop", artist: "Elena Rodriguez" },
          { id: 2, title: "Ocean Waves", description: "Serene seascape with rolling waves", price: 320.00, category: "painting", image_url: "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400&h=300&fit=crop", artist: "Marcus Chen" },
          { id: 3, title: "Urban Jungle", description: "Modern cityscape with vibrant colors", price: 275.00, category: "painting", image_url: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop", artist: "Sofia Martinez" },
          { id: 4, title: "Golden Hour", description: "Warm sunset landscape painting", price: 380.00, category: "painting", image_url: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop", artist: "David Kim" },
          { id: 5, title: "Digital Cosmos", description: "Futuristic space digital art", price: 199.99, category: "digital", image_url: "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=400&h=300&fit=crop", artist: "Alex Turner" },
          { id: 6, title: "Forest Whispers", description: "Mystical forest scene", price: 425.00, category: "painting", image_url: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop", artist: "Luna Park" },
          { id: 7, title: "Neon Dreams", description: "Cyberpunk inspired digital artwork", price: 250.00, category: "digital", image_url: "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=300&fit=crop", artist: "Neo Smith" },
          { id: 8, title: "Mountain Peak", description: "Majestic mountain landscape", price: 350.00, category: "painting", image_url: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop", artist: "River Stone" },
          { id: 9, title: "Abstract Flow", description: "Fluid abstract composition", price: 290.00, category: "painting", image_url: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop", artist: "Maya Blue" },
          { id: 10, title: "City Lights", description: "Night cityscape photography", price: 180.00, category: "photography", image_url: "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop", artist: "James Wright" },
          { id: 11, title: "Floral Burst", description: "Vibrant flower arrangement", price: 220.00, category: "painting", image_url: "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=300&fit=crop", artist: "Rose Garden" },
          { id: 12, title: "Geometric Harmony", description: "Modern geometric composition", price: 310.00, category: "digital", image_url: "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=300&fit=crop", artist: "Vector Art" },
          { id: 13, title: "Desert Sunset", description: "Warm desert landscape at dusk", price: 395.00, category: "painting", image_url: "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?w=400&h=300&fit=crop", artist: "Sand Walker" },
          { id: 14, title: "Underwater World", description: "Deep sea marine life scene", price: 340.00, category: "painting", image_url: "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=300&fit=crop", artist: "Ocean Deep" },
          { id: 15, title: "Vintage Portrait", description: "Classic portrait in sepia tones", price: 480.00, category: "photography", image_url: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop", artist: "Time Keeper" },
          { id: 16, title: "Space Nebula", description: "Cosmic nebula digital artwork", price: 265.00, category: "digital", image_url: "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=400&h=300&fit=crop", artist: "Star Gazer" }
        ];
        
        const artwork = testArtworks.find(art => art.id === artworkId);
        if (artwork) {
          currentCart.items.push({
            artwork_id: artworkId,
            quantity: quantity,
            artwork: artwork
          });
        }
      }
      
      localStorage.setItem('cart', JSON.stringify(currentCart));
      setCart(currentCart);
      toast.success('Added to cart');
      return { success: true };
    } catch (error) {
      toast.error('Failed to add to cart');
      return { success: false, error: error.message };
    }
  };

  const updateQuantity = async (artworkId, quantity) => {
    try {
      const data = await apiRequest(`/api/cart/${artworkId}`, {
        method: 'PATCH',
        body: JSON.stringify({ quantity }),
      });
      setCart(data);
      if (quantity === 0) {
        toast.success('Removed from cart');
      } else {
        toast.success('Cart updated');
      }
    } catch (error) {
      toast.error('Failed to update cart');
    }
  };

  const removeFromCart = async (artworkId) => {
    try {
      const data = await apiRequest(`/api/cart/${artworkId}`, {
        method: 'DELETE',
      });
      setCart(data);
      toast.success('Removed from cart');
    } catch (error) {
      toast.error('Failed to remove from cart');
    }
  };

  const clearCart = async () => {
    try {
      // Remove all items from cart
      if (cart?.items) {
        for (const item of cart.items) {
          await removeFromCart(item.artwork_id);
        }
      }
      setCart({ items: [] });
      toast.success('Cart cleared');
    } catch (error) {
      toast.error('Failed to clear cart');
    }
  };

  // Calculate cart statistics
  const cartCount = cart?.items?.reduce((total, item) => total + item.quantity, 0) || 0;
  const cartTotal = cart?.items?.reduce((total, item) => total + (item.artwork?.price * item.quantity), 0) || 0;
  const cartItems = cart?.items || [];

  const value = {
    cart,
    loading,
    cartCount,
    cartTotal,
    cartItems,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    refreshCart: fetchCart,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};