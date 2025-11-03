import React, { useState, useEffect } from 'react';
import { Package, Truck, MapPin, Clock, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import '../styles/pages/Delivery.css';

export default function Delivery() {
  const { user } = useAuth();
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDeliveries();
  }, []);

  const fetchDeliveries = async () => {
    try {
      // Mock delivery data for now
      const mockDeliveries = [
        {
          id: 1,
          orderId: 'ORD-001',
          artworkTitle: 'Starry Night Dreams',
          artist: 'Elena Rodriguez',
          status: 'shipped',
          trackingNumber: 'TRK123456789',
          estimatedDelivery: '2024-01-15',
          shippingAddress: '123 Art Street, Creative City, CC 12345',
          carrier: 'ArtExpress',
          price: 450.00
        },
        {
          id: 2,
          orderId: 'ORD-002',
          artworkTitle: 'Ocean Waves',
          artist: 'Marcus Chen',
          status: 'processing',
          trackingNumber: null,
          estimatedDelivery: '2024-01-18',
          shippingAddress: '123 Art Street, Creative City, CC 12345',
          carrier: 'ArtExpress',
          price: 320.00
        }
      ];
      setDeliveries(mockDeliveries);
    } catch (error) {
      console.error('Error fetching deliveries:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'processing':
        return <Package className="status-icon processing" size={20} />;
      case 'shipped':
        return <Truck className="status-icon shipped" size={20} />;
      case 'delivered':
        return <CheckCircle className="status-icon delivered" size={20} />;
      default:
        return <Clock className="status-icon" size={20} />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'processing':
        return 'Processing';
      case 'shipped':
        return 'Shipped';
      case 'delivered':
        return 'Delivered';
      default:
        return 'Pending';
    }
  };

  if (loading) {
    return (
      <div className="delivery-page">
        <div className="loading">Loading deliveries...</div>
      </div>
    );
  }

  return (
    <div className="delivery-page">
      <div className="delivery-container">
        <div className="delivery-header">
          <h1 className="delivery-title">My Deliveries</h1>
          <p className="delivery-subtitle">Track your artwork deliveries</p>
        </div>

        {deliveries.length === 0 ? (
          <div className="empty-deliveries">
            <Package size={64} className="empty-icon" />
            <h3>No deliveries yet</h3>
            <p>Your artwork deliveries will appear here once you place orders.</p>
          </div>
        ) : (
          <div className="deliveries-list">
            {deliveries.map((delivery) => (
              <div key={delivery.id} className="delivery-card">
                <div className="delivery-header-info">
                  <div className="delivery-status">
                    {getStatusIcon(delivery.status)}
                    <span className={`status-text ${delivery.status}`}>
                      {getStatusText(delivery.status)}
                    </span>
                  </div>
                  <div className="order-info">
                    <span className="order-id">Order #{delivery.orderId}</span>
                    <span className="price">${delivery.price.toFixed(2)}</span>
                  </div>
                </div>

                <div className="delivery-content">
                  <div className="artwork-info">
                    <h3 className="artwork-title">{delivery.artworkTitle}</h3>
                    <p className="artist-name">by {delivery.artist}</p>
                  </div>

                  <div className="delivery-details">
                    <div className="detail-row">
                      <MapPin size={16} className="detail-icon" />
                      <div>
                        <span className="detail-label">Shipping Address:</span>
                        <span className="detail-value">{delivery.shippingAddress}</span>
                      </div>
                    </div>

                    <div className="detail-row">
                      <Truck size={16} className="detail-icon" />
                      <div>
                        <span className="detail-label">Carrier:</span>
                        <span className="detail-value">{delivery.carrier}</span>
                      </div>
                    </div>

                    {delivery.trackingNumber && (
                      <div className="detail-row">
                        <Package size={16} className="detail-icon" />
                        <div>
                          <span className="detail-label">Tracking Number:</span>
                          <span className="detail-value tracking-number">
                            {delivery.trackingNumber}
                          </span>
                        </div>
                      </div>
                    )}

                    <div className="detail-row">
                      <Clock size={16} className="detail-icon" />
                      <div>
                        <span className="detail-label">Estimated Delivery:</span>
                        <span className="detail-value">
                          {new Date(delivery.estimatedDelivery).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  {delivery.status === 'shipped' && (
                    <div className="tracking-actions">
                      <button 
                        className="track-btn"
                        onClick={() => {
                          // Bolt app deep link (for ride/delivery requests)
                          const boltAppUrl = `bolt://request?pickup=${encodeURIComponent(delivery.shippingAddress)}&destination=Art Gallery Warehouse`;
                          
                          // Fallback to Bolt website
                          const boltWebUrl = 'https://bolt.eu/en/cities/';
                          
                          // Try to open Bolt app
                          const iframe = document.createElement('iframe');
                          iframe.style.display = 'none';
                          iframe.src = boltAppUrl;
                          document.body.appendChild(iframe);
                          
                          // Remove iframe after attempt
                          setTimeout(() => {
                            document.body.removeChild(iframe);
                          }, 1000);
                          
                          // Show fallback options
                          setTimeout(() => {
                            if (confirm('Bolt app not found. Open Bolt website to download the app?')) {
                              window.open(boltWebUrl, '_blank');
                            }
                          }, 2000);
                        }}
                      >
                        Track with Bolt
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}