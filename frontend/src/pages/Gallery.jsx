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
      setArtworks(artworksList);
    } catch (err) {
      setError('Error loading artworks');
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
