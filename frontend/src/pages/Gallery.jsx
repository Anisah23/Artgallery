import React, { useState, useEffect } from 'react';
import ArtworkCard from '../components/ArtworkCard';
import CategoryFilter from '../components/CategoryFilter';
import ArtworkModal from '../components/ArtworkModal';
import { apiRequest } from '../utils/api';
import '../styles/components/Gallery.css';
import '../styles/components/GalleryStats.css';

export default function Gallery() {
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [artworks, setArtworks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchArtworks();
  }, []);

  const fetchArtworks = async () => {
    try {
      const data = await apiRequest('/api/gallery');
      // Handle both paginated and simple array responses
      const artworksList = data.items || data || [];
      
      // If no artworks from API, use test data
      if (artworksList.length === 0) {
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
        setArtworks(testArtworks);
      } else {
        setArtworks(artworksList);
      }
    } catch (err) {
      // On error, show test artworks
      const testArtworks = [
        { id: 1, title: "Starry Night Dreams", description: "Abstract interpretation of Van Gogh's masterpiece", price: 450.00, category: "painting", image_url: "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=400&h=300&fit=crop", artist: "Elena Rodriguez" }
      ];
      setArtworks(testArtworks);
      console.error('Error fetching artworks:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredArtworks = selectedCategory === 'All Categories'
    ? artworks
    : artworks.filter(artwork =>
        artwork.category.toLowerCase() === selectedCategory.toLowerCase()
      );

  if (loading) {
    return (
      <div className="gallery-container page">
        <div className="loading">Loading artworks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="gallery-container page">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="gallery-container page">
      <div className="gallery-header">
        <div>
          <h1 className="gallery-title">Art Gallery</h1>
          <p className="gallery-description">Discover unique artworks from talented artists worldwide</p>
          <p className="gallery-stats">{artworks.length} artworks available</p>
        </div>
        <CategoryFilter onSelect={setSelectedCategory} />
      </div>

      <div className="art-gallery">
        <div className="grid">
          {filteredArtworks.length === 0 ? (
            <p className="no-artworks">No artworks found in this category.</p>
          ) : (
            filteredArtworks.map((artwork) => (
              <ArtworkCard key={artwork.id} artwork={artwork} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
