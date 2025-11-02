import React, { useState, useEffect } from 'react';
import { apiRequest } from '../utils/api';

const CategoryFilter = ({ onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [categories, setCategories] = useState(['All Categories']);
  const [selectedCategory, setSelectedCategory] = useState('All Categories');

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const data = await apiRequest('/api/gallery');
      // Handle both paginated and simple array responses
      const artworks = data.items || data || [];
      const uniqueCategories = [...new Set(artworks.map(artwork => 
        artwork.category.charAt(0).toUpperCase() + artwork.category.slice(1)
      ))];
      setCategories(['All Categories', ...uniqueCategories.sort()]);
    } catch (error) {
      console.error('Error fetching categories:', error);
      // Fallback to default categories
      setCategories([
        'All Categories',
        'Painting',
        'Sculpture', 
        'Photography',
        'Digital',
        'Mixed Media'
      ]);
    }
  };

  return (
    <div className="gallery-filter">
      <button 
        className="filter-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        {selectedCategory}
        <svg 
          width="20" 
          height="20" 
          viewBox="0 0 20 20" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2"
        >
          <path d="M6 8l4 4 4-4" />
        </svg>
      </button>
      
      {isOpen && (
        <div className="filter-dropdown">
          {categories.map((category) => (
            <button
              key={category}
              className="filter-option"
              onClick={() => {
                setSelectedCategory(category);
                onSelect(category);
                setIsOpen(false);
              }}
            >
              {category}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default CategoryFilter;