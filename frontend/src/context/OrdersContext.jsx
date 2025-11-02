import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { apiRequest } from '../utils/api';

const OrdersContext = createContext();

export const useOrders = () => {
  return useContext(OrdersContext);
};

export const OrdersProvider = ({ children }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const { isLoggedIn } = useAuth();

  // Load orders from API when user is logged in
  useEffect(() => {
    if (isLoggedIn) {
      fetchOrders();
    } else {
      setOrders([]);
    }
  }, [isLoggedIn]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/api/orders');
      setOrders(data.items || []);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const addOrder = (orderData) => {
    // This will be called after successful API order creation
    fetchOrders(); // Refresh orders from API
  };

  const updateOrderStatus = async (orderId, newStatus) => {
    try {
      await apiRequest(`/api/orders/${orderId}`, {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus }),
      });
      // Refresh orders after status update
      await fetchOrders();
    } catch (error) {
      console.error('Error updating order status:', error);
      throw error;
    }
  };

  const value = {
    orders,
    loading,
    addOrder,
    updateOrderStatus,
    fetchOrders,
  };

  return <OrdersContext.Provider value={value}>{children}</OrdersContext.Provider>;
};
