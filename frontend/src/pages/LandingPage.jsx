import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import landingImage from "../assets/pasted-image.png";
import "../styles/pages/LandingPage.css";

export default function LandingPage() {
  const { isLoggedIn, role } = useAuth();
  const navigate = useNavigate();

  const handleGetStarted = () => {
    if (isLoggedIn) {
      navigate('/gallery');
    } else {
      navigate('/auth');
    }
  };
  return (
    <div className="landing-page">
      <div className="landing-content">
        <div
          className="landing-hero"
          style={{ backgroundImage: `url(${landingImage})` }}
        >
          <div className="landing-hero-overlay">
            <h1 className="landing-title">
              L'art du <br /> monde entier
            </h1>
          </div>
        </div>

        <div className="landing-footer">
        </div>

        <div className="welcome-section">
          <div className="welcome-container">
            <h2 className="welcome-header">Welcome to the World of Art</h2>
            <p className="welcome-subheading">Discover unique pieces from talented artisans around the globe</p>
            <button className="get-started-btn" onClick={handleGetStarted}>Get Started</button>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">🎨</div>
                <h3 className="feature-title">For Artisans</h3>
                <p className="feature-description">Showcase your artwork to collectors worldwide and manage your portfolio</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">🖼️</div>
                <h3 className="feature-title">For Collectors</h3>
                <p className="feature-description">Browse unique art pieces, create wishlists, and purchase with ease</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">🚚</div>
                <h3 className="feature-title">Secure Delivery</h3>
                <p className="feature-description">Safe and insured delivery of your precious art pieces to your doorstep</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

