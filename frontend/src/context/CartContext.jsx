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
      const data = await apiRequest('/api/cart/');
      setCart(data);
    } catch (error) {
      console.error('Error fetching cart:', error);
      // If cart doesn't exist, create an empty cart structure
      setCart({ items: [] });
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (artworkId, quantity = 1) => {
    try {
      const data = await apiRequest('/api/cart/', {
        method: 'POST',
        body: JSON.stringify({ artworkId, quantity }),
      });
      setCart(data);
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