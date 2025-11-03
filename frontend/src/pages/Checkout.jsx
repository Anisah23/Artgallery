import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiRequest } from '../utils/api';
import '../styles/pages/Checkout.css';

const CheckoutForm = ({ cartItems, shippingInfo, totalAmount, onSuccess, onError }) => {
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Validate required shipping information
    const requiredFields = ['fullName', 'email', 'address', 'city', 'postalCode', 'country'];
    const missingFields = requiredFields.filter(field => !shippingInfo[field]?.trim());
    
    if (missingFields.length > 0) {
      onError(`Please fill in all required fields: ${missingFields.join(', ')}`);
      return;
    }

    setProcessing(true);
    try {
      // Create order without payment processing (temporary)
      await createOrder();
    } catch (error) {
      console.error('Order creation error:', error);
      onError('Order creation failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const createOrder = async () => {
    try {
      const orderData = {
        items: cartItems.map(item => ({
          artwork_id: item.artwork_id || item.id,
          quantity: item.quantity,
          price: item.artwork?.price || item.price
        })),
        shipping_details: {
          fullName: shippingInfo.fullName,
          address: shippingInfo.address,
          city: shippingInfo.city,
          postalCode: shippingInfo.postalCode,
          country: shippingInfo.country
        },
        total_amount: totalAmount,
        payment_status: 'pending' // Temporary status
      };

      const response = await apiRequest('/api/orders', {
        method: 'POST',
        body: JSON.stringify(orderData)
      });

      onSuccess(response);
    } catch (error) {
      console.error('Order creation error:', error);
      onError(error.message || 'Failed to create order. Please contact support.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="checkout-form">
      <div className="checkout-grid">
        <div className="checkout-section">
          <h2 className="section-title">Shipping Information</h2>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              value={shippingInfo.fullName}
              onChange={(e) => shippingInfo.onChange('fullName', e.target.value)}
              className="form-input"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              value={shippingInfo.email}
              onChange={(e) => shippingInfo.onChange('email', e.target.value)}
              className="form-input"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Address</label>
            <input
              type="text"
              value={shippingInfo.address}
              onChange={(e) => shippingInfo.onChange('address', e.target.value)}
              className="form-input"
              required
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">City</label>
              <input
                type="text"
                value={shippingInfo.city}
                onChange={(e) => shippingInfo.onChange('city', e.target.value)}
                className="form-input"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Postal Code</label>
              <input
                type="text"
                value={shippingInfo.postalCode}
                onChange={(e) => shippingInfo.onChange('postalCode', e.target.value)}
                className="form-input"
                required
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Country</label>
            <input
              type="text"
              value={shippingInfo.country}
              onChange={(e) => shippingInfo.onChange('country', e.target.value)}
              className="form-input"
              required
            />
          </div>
        </div>

        <div className="checkout-section payment">
          <h2 className="section-title">Payment Information</h2>
          <div className="form-group">
            <div className="payment-notice">
              <p>Payment processing is temporarily disabled. Your order will be created with pending payment status.</p>
            </div>
          </div>
        </div>

        <div className="checkout-section summary">
          <h2 className="section-title">Order Summary</h2>
          <div className="order-items">
            {cartItems.map(item => {
              const artwork = item.artwork || item;
              const price = artwork.price || 0;
              return (
                <div key={item.artwork_id || item.id} className="order-item">
                  <div className="order-item-info">
                    <h4 className="order-item-title">{artwork.title}</h4>
                    <p className="order-item-artist">{artwork.artist || 'Unknown Artist'}</p>
                    <p className="order-item-quantity">Quantity: {item.quantity}</p>
                  </div>
                  <p className="order-item-price">${(price * item.quantity).toFixed(2)}</p>
                </div>
              );
            })}
          </div>
          <div className="order-total">
            <span>Total: ${totalAmount.toFixed(2)}</span>
          </div>
        </div>
      </div>

      <div className="checkout-actions">
        <button
          type="submit"
          className="btn-primary"
          disabled={processing}
        >
          {processing ? 'Processing...' : `Create Order - $${totalAmount.toFixed(2)}`}
        </button>
      </div>
    </form>
  );
};

export default function Checkout() {
  const [cartItems, setCartItems] = useState([]);
  const [shippingInfo, setShippingInfo] = useState({
    fullName: '',
    email: '',
    address: '',
    city: '',
    postalCode: '',
    country: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const localCart = JSON.parse(localStorage.getItem('cart') || '{"items": []}');
      setCartItems(localCart.items || []);
    } catch (error) {
      console.error('Error fetching cart:', error);
      setCartItems([]);
    } finally {
      setLoading(false);
    }
  };

  const handleShippingChange = (field, value) => {
    setShippingInfo(prev => ({ ...prev, [field]: value }));
  };

  const getTotalPrice = () => {
    return cartItems.reduce((total, item) => {
      const price = item.artwork?.price || item.price || 0;
      return total + (price * item.quantity);
    }, 0);
  };

  const handlePaymentSuccess = (order) => {
    // Clear cart and navigate to orders
    localStorage.setItem('cart', JSON.stringify({items: []}));
    setCartItems([]);
    navigate('/orders', { 
      state: { newOrder: order },
      replace: true 
    });
  };

  const handlePaymentError = (errorMessage) => {
    setError(errorMessage);
  };

  if (loading) {
    return (
      <div className="checkout-page">
        <div className="loading">Loading checkout...</div>
      </div>
    );
  }

  if (cartItems.length === 0) {
    return (
      <div className="checkout-page">
        <div className="empty-checkout">
          <h2 className="empty-title">Your cart is empty</h2>
          <p className="empty-text">Add some items to your cart before checking out.</p>
          <button onClick={() => navigate('/gallery')} className="btn-primary">
            Browse Gallery
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="checkout-page page">
      <div className="checkout-container">
        <div className="checkout-header">
          <h1 className="checkout-title">Checkout</h1>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <CheckoutForm
          cartItems={cartItems}
          shippingInfo={{ ...shippingInfo, onChange: handleShippingChange }}
          totalAmount={getTotalPrice()}
          onSuccess={handlePaymentSuccess}
          onError={handlePaymentError}
        />
      </div>
    </div>
  );
}
