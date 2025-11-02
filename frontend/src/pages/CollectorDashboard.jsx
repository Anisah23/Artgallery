import React, { useState, useEffect } from 'react';
import { Heart, ShoppingCart, Package } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useWishlist } from '../context/WishlistContext';
import { apiRequest } from '../utils/api';
import '../styles/pages/CollectorDashboard.css';

export default function CustomerDashboard() {
  const { user } = useAuth();
  const { wishlistCount } = useWishlist();
  const [stats, setStats] = useState({
    totalPurchases: 0,
    activeOrders: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const orders = await apiRequest('/api/orders');
      const orderItems = orders.items || [];
      
      const totalPurchases = orderItems.filter(order => 
        ['delivered', 'completed'].includes(order.status)
      ).length;
      
      const activeOrders = orderItems.filter(order => 
        ['pending', 'confirmed', 'processing', 'shipped'].includes(order.status)
      ).length;
      
      setStats({ totalPurchases, activeOrders });
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="collector-dashboard">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1 className="dashboard-title">Collector Dashboard</h1>
          <p className="dashboard-subtitle">Welcome back, {user?.fullName || 'art enthusiast'}!</p>
        </div>

        <div className="dashboard-stats">
          <div className="dashboard-card">
            <div className="card-header">
              <h3 className="card-title">Wishlist Items</h3>
              <Heart className="card-icon" size={20} />
            </div>
            <div className="card-content">
              <div className="card-value">{wishlistCount}</div>
              <p className="card-description">Items you're interested in</p>
            </div>
          </div>

          <div className="dashboard-card">
            <div className="card-header">
              <h3 className="card-title">Total Purchases</h3>
              <ShoppingCart className="card-icon" size={20} />
            </div>
            <div className="card-content">
              <div className="card-value">{loading ? '...' : stats.totalPurchases}</div>
              <p className="card-description">Artworks purchased</p>
            </div>
          </div>

          <div className="dashboard-card">
            <div className="card-header">
              <h3 className="card-title">Active Orders</h3>
              <Package className="card-icon" size={20} />
            </div>
            <div className="card-content">
              <div className="card-value">{loading ? '...' : stats.activeOrders}</div>
              <p className="card-description">In transit to you</p>
            </div>
          </div>
        </div>

        <div className="dashboard-lower">
          <div className="dashboard-card">
            <div className="card-header">
              <h3 className="card-title">Recent Activity</h3>
            </div>
            <div className="card-content">
              <p className="empty-text">No recent activity</p>
            </div>
          </div>

          <div className="dashboard-card">
            <div className="card-header">
              <h3 className="card-title">Recommended for You</h3>
            </div>
            <div className="card-content">
              <p className="empty-text">
                Browse the gallery to get personalized recommendations
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
