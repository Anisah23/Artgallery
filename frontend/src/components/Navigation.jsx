import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useWishlist } from "../context/WishlistContext";
import "../styles/components/Navigation.css";

export default function Navigation() {
  const { isLoggedIn, role, logout } = useAuth();
  const { wishlistCount } = useWishlist();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="nav">
      <div className="nav-container">
        <Link to="/" className="nav-title-link">
          <h1 className="nav-title">L'art du vrai soi</h1>
        </Link>

        <div className="nav-links">
          {isLoggedIn && (
            <>
              <Link
                to="/gallery"
                className={`nav-link ${location.pathname === '/gallery' ? 'active' : ''}`}
              >
                Gallery
              </Link>
              <Link
                to={role === 'Artist' ? '/dashboard/artist' : '/dashboard/collector'}
                className={`nav-link ${location.pathname.startsWith('/dashboard') ? 'active' : ''}`}
              >
                Dashboard
              </Link>
              {role === 'Collector' && (
                <>
                  <Link
                    to="/wishlist"
                    className={`nav-link ${location.pathname === '/wishlist' ? 'active' : ''}`}
                  >
                    Wishlist
                  </Link>
                  <Link
                    to="/orders"
                    className={`nav-link ${location.pathname === '/orders' ? 'active' : ''}`}
                  >
                    Orders
                  </Link>
                  <Link
                    to="/cart"
                    className={`nav-link ${location.pathname === '/cart' ? 'active' : ''}`}
                  >
                    Cart
                  </Link>
                </>
              )}
              <Link
                to="/notifications"
                className={`nav-link ${location.pathname === '/notifications' ? 'active' : ''}`}
              >
                Notifications
              </Link>
            </>
          )}
        </div>

        <div className="nav-icons">
          {isLoggedIn ? (
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          ) : (
            <Link to="/auth" className="logout-btn">
              Sign In / Sign Up
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
