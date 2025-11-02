import React, { useState, useEffect } from "react";
import { Plus, Edit, Trash2, Package, DollarSign } from "lucide-react";
import { useAuth } from '../context/AuthContext';
import { apiRequest, uploadImage } from '../utils/api';
import "../styles/pages/ArtistDashboard.css";
import "../styles/pages/ImageUpload.css";
import "../styles/components/ImageFix.css";
import "../styles/pages/OrdersTab.css";

export default function ArtistDashboard() {
  const { user } = useAuth();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [category, setCategory] = useState("");
  const [image, setImage] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [uploadMethod, setUploadMethod] = useState("url");
  const [artworks, setArtworks] = useState([]);
  const [orders, setOrders] = useState([]);
  const [activeTab, setActiveTab] = useState('artworks');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [stats, setStats] = useState({
    salesThisMonth: 0,
    totalValue: 0
  });

  useEffect(() => {
    fetchArtworks();
    fetchStats();
  }, []);

  const fetchArtworks = async () => {
    try {
      const data = await apiRequest('/api/artist/artworks');
      setArtworks(data?.items || data || []);
    } catch (error) {
      console.error('Error fetching artworks:', error);
      setArtworks([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const orders = await apiRequest('/api/orders');
      const orderItems = orders.items || [];
      
      // Calculate sales this month
      const currentMonth = new Date().getMonth();
      const currentYear = new Date().getFullYear();
      
      const salesThisMonth = orderItems.filter(order => {
        const orderDate = new Date(order.created_at);
        return orderDate.getMonth() === currentMonth && 
               orderDate.getFullYear() === currentYear &&
               ['delivered', 'completed'].includes(order.status);
      }).length;
      
      setStats({
        salesThisMonth,
        totalValue: myArtworks.reduce((sum, art) => sum + art.price, 0)
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const myArtworks = artworks;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    
    try {
      let imageUrl = image;
      
      // If uploading file, upload to Cloudinary first
      if (uploadMethod === "upload" && imageFile) {
        const uploadResult = await uploadImage(imageFile);
        imageUrl = uploadResult.image_url;
      }

      await apiRequest('/api/artist/artworks', {
        method: 'POST',
        body: JSON.stringify({
          title,
          description,
          price: parseFloat(price),
          category,
          image_url: imageUrl
        })
      });

      // Reset form
      setTitle("");
      setDescription("");
      setPrice("");
      setCategory("");
      setImage("");
      setImageFile(null);
      setUploadMethod("url");
      setIsDialogOpen(false);

      // Refresh artworks
      fetchArtworks();
    } catch (error) {
      console.error('Error adding artwork:', error);
      alert('Error adding artwork. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteArt = async (id) => {
    try {
      await apiRequest(`/api/artist/artworks/${id}`, {
        method: 'DELETE'
      });
      fetchArtworks();
    } catch (error) {
      console.error('Error deleting artwork:', error);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Artist Dashboard</h1>
          <p className="dashboard-subtitle">Manage your art collection</p>
        </div>
        <button
          className="add-art-btn"
          onClick={() => setIsDialogOpen(true)}
        >
          <Plus className="icon" size={20} />
          Add New Artwork
        </button>
      </div>

      {isDialogOpen && (
        <div className="dialog-overlay">
          <div className="dialog">
            <h2 className="dialog-title">Add New Artwork</h2>
            <p className="dialog-description">
              Share your latest creation with collectors worldwide
            </p>
            <form onSubmit={handleSubmit} className="dialog-form">
              <label>Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter artwork title"
                required
              />

              <label>Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe your artwork"
                rows="4"
                required
              ></textarea>

              <div className="form-row">
                <div>
                  <label>Price ($)</label>
                  <input
                    type="number"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    placeholder="0.00"
                    step="0.01"
                    required
                  />
                </div>
                <div>
                  <label>Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    required
                  >
                    <option value="">Select category</option>
                    <option value="painting">Painting</option>
                    <option value="sculpture">Sculpture</option>
                    <option value="photography">Photography</option>
                    <option value="digital">Digital Art</option>
                    <option value="mixed-media">Mixed Media</option>
                    <option value="textile">Textile Art</option>
                  </select>
                </div>
              </div>

              <label>Artwork Image</label>
              <div className="image-upload-section">
                <div className="upload-method-selector">
                  <label>
                    <input
                      type="radio"
                      value="url"
                      checked={uploadMethod === "url"}
                      onChange={(e) => setUploadMethod(e.target.value)}
                    />
                    Use Image URL
                  </label>
                  <label>
                    <input
                      type="radio"
                      value="upload"
                      checked={uploadMethod === "upload"}
                      onChange={(e) => setUploadMethod(e.target.value)}
                    />
                    Upload Image
                  </label>
                </div>
                
                {uploadMethod === "url" ? (
                  <input
                    type="text"
                    value={image}
                    onChange={(e) => setImage(e.target.value)}
                    placeholder="Enter image URL"
                    required={uploadMethod === "url"}
                  />
                ) : (
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setImageFile(e.target.files[0])}
                    required={uploadMethod === "upload"}
                  />
                )}
              </div>

              <button type="submit" className="submit-btn" disabled={uploading}>
                {uploading ? 'Uploading...' : 'Add Artwork'}
              </button>
              <button
                type="button"
                className="cancel-btn"
                onClick={() => setIsDialogOpen(false)}
              >
                Cancel
              </button>
            </form>
          </div>
        </div>
      )}

      <div className="stats-card">
        <h3>Your Statistics</h3>
        <div className="stats">
          <div>
            <p className="highlight">{myArtworks.length}</p>
            <span>Total Artworks</span>
          </div>
          <div>
            <p className="highlight">{stats.salesThisMonth}</p>
            <span>Sales This Month</span>
          </div>
          <div>
            <p className="highlight">
              ${myArtworks.reduce((sum, art) => sum + art.price, 0).toFixed(2)}
            </p>
            <span>Total Value</span>
          </div>
        </div>
      </div>

      <h2 className="section-title">Your Artworks</h2>
      {loading ? (
        <div className="empty-state">
          <p>Loading artworks...</p>
        </div>
      ) : myArtworks.length === 0 ? (
        <div className="empty-state">
          <p>Unable to load artworks. Please refresh the page.</p>
          <button
            onClick={() => setIsDialogOpen(true)}
            className="add-art-btn"
          >
            Add Your First Artwork
          </button>
        </div>
      ) : (
        <div className="art-grid">
          {myArtworks.map((art) => (
            <div key={art.id} className="art-card">
              <img src={art.image_url || art.image} alt={art.title} className="art-image" />
              <div className="art-content">
                <h3>{art.title}</h3>
                <p className="description">{art.description}</p>
                <div className="art-meta">
                  <span className="price">${art.price}</span>
                  <span className="category">{art.category}</span>
                </div>
                <div className="art-actions">
                  <button className="edit-btn">
                    <Edit size={16} />
                    Edit
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteArt(art.id)}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
