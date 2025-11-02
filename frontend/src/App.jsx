import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { WishlistProvider } from './context/WishlistContext';
import { AuthProvider } from './context/AuthContext';
import { OrdersProvider } from './context/OrdersContext';
import { CartProvider } from './context/CartContext';
import Navigation from './components/Navigation';
import LandingPage from './pages/LandingPage';
import Auth from './pages/Auth';
import Gallery from './pages/Gallery';
import Wishlist from './pages/Wishlist';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Orders from './pages/Orders';
import Notifications from './pages/Notifications';
import CollectorDashboard from './pages/CollectorDashboard';
import ArtistDashboard from './pages/ArtistDashboard';

import './App.css';

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <WishlistProvider>
          <OrdersProvider>
            <Router>
              <div className="app">
                <Navigation />
                <main className="main-content">
                  <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/auth" element={<Auth />} />
                    <Route path="/login" element={<Auth initialMode="login" />} />
                    <Route path="/gallery" element={<Gallery />} />

                    <Route path="/wishlist" element={<Wishlist />} />
                    <Route path="/cart" element={<Cart />} />
                    <Route path="/checkout" element={<Checkout />} />
                    <Route path="/orders" element={<Orders />} />
                    <Route path="/notifications" element={<Notifications />} />
                    <Route path="/dashboard/collector" element={<CollectorDashboard />} />
                    <Route path="/dashboard/artist" element={<ArtistDashboard />} />
                    <Route path="/artwork/*" element={<Navigate to="/gallery" replace />} />
                  </Routes>
                </main>
              </div>
            </Router>
          </OrdersProvider>
        </WishlistProvider>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;