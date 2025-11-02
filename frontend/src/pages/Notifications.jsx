import React, { useState, useEffect } from "react";
import {
  Bell,
  Package,
  Heart,
  ShoppingCart,
  Paintbrush,
  CheckCircle,
  Trash2,
} from "lucide-react";
import { apiRequest } from "../utils/api";
import { useAuth } from "../context/AuthContext";
import "../styles/pages/Notifications.css";

export default function Notifications() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("all");

  // Determine API endpoint based on user role
  const getNotificationsEndpoint = () => {
    if (!user) return null;
    // Both roles use the same collectors endpoint for now
    return "/api/collectors/notifications";
  };

  // Fetch notifications whenever user changes
  useEffect(() => {
    if (user) fetchNotifications();
  }, [user]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const endpoint = getNotificationsEndpoint();
      if (!endpoint) return;
      const data = await apiRequest(endpoint);
      setNotifications(data);
    } catch (err) {
      setError(err.message || err?.error || "Failed to load notifications");
    } finally {
      setLoading(false);
    }
  };

  const patchNotification = async (id, body) => {
    // Use collectors endpoint for both roles for now
    const endpoint = `/api/collectors/notifications/${id}`;
    return apiRequest(endpoint, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  };

  const onMarkAsRead = async (id) => {
    try {
      await patchNotification(id, { read: true });
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read: true } : n))
      );
    } catch (err) {
      console.error("Failed to mark notification as read:", err);
    }
  };

  const onMarkAllAsRead = async () => {
    try {
      const unread = notifications.filter((n) => !n.read);
      await Promise.all(unread.map((n) => patchNotification(n.id, { read: true })));
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    } catch (err) {
      console.error("Failed to mark all notifications as read:", err);
    }
  };

  const onDeleteNotification = async (id) => {
    try {
      // Use collectors endpoint for both roles for now
      const endpoint = `/api/collectors/notifications/${id}`;
      await apiRequest(endpoint, { method: "DELETE" });
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    } catch (err) {
      console.error("Failed to delete notification:", err);
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case "order":
        return <ShoppingCart className="icon gold" size={24} />;
      case "delivery":
        return <Package className="icon green" size={24} />;
      case "wishlist":
        return <Heart className="icon red" size={24} />;
      case "new-art":
        return <Paintbrush className="icon maroon" size={24} />;
      default:
        return <Bell className="icon gold" size={24} />;
    }
  };

  const formatTimestamp = (dateString) => {
    const now = new Date();
    const date = new Date(dateString);
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes} minute${minutes !== 1 ? "s" : ""} ago`;
    if (hours < 24) return `${hours} hour${hours !== 1 ? "s" : ""} ago`;
    if (days < 7) return `${days} day${days !== 1 ? "s" : ""} ago`;
    return date.toLocaleDateString();
  };

  const unreadCount = notifications.filter((n) => !n.read).length;
  const orderNotifications = notifications.filter(
    (n) => n.type === "order" || n.type === "delivery"
  );
  const artNotifications = notifications.filter(
    (n) => n.type === "new-art" || n.type === "wishlist"
  );

  const getFilteredNotifications = () => {
    switch (activeTab) {
      case "orders":
        return orderNotifications;
      case "artworks":
        return artNotifications;
      default:
        return notifications;
    }
  };

  const NotificationCard = ({ notification }) => (
    <div className={`notification-card ${!notification.read ? "unread" : ""}`}>
      <div className="notification-content">
        <div className="notification-icon">{getIcon(notification.type)}</div>
        <div className="notification-body">
          <div className="notification-header">
            <div>
              <h3 className="notification-title">{notification.title}</h3>
              <p className="notification-message">{notification.message}</p>
            </div>
            <button
              onClick={() => onDeleteNotification(notification.id)}
              className="delete-btn"
            >
              <Trash2 size={16} />
            </button>
          </div>
          <div className="notification-footer">
            <span className="timestamp">{formatTimestamp(notification.timestamp)}</span>
            {!notification.read && (
              <button
                className="mark-read-btn"
                onClick={() => onMarkAsRead(notification.id)}
              >
                <CheckCircle size={14} className="check-icon" />
                Mark as Read
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  if (loading)
    return (
      <div className="notifications-container">
        <div className="notifications-content">
          <h1 className="page-title">Notifications</h1>
          <p>Loading notifications...</p>
        </div>
      </div>
    );

  if (error)
    return (
      <div className="notifications-container">
        <div className="notifications-content">
          <h1 className="page-title">Notifications</h1>
          <p style={{ color: "red" }}>{error}</p>
        </div>
      </div>
    );

  return (
    <div className="notifications-container">
      <div className="notifications-content">
        <div className="notifications-header">
          <div>
            <h1 className="page-title">Notifications</h1>
            <p>
              {unreadCount > 0 ? (
                <>
                  You have <span className="badge">{unreadCount}</span> unread
                  notification{unreadCount !== 1 ? "s" : ""}
                </>
              ) : (
                "All caught up!"
              )}
            </p>
          </div>
          {unreadCount > 0 && (
            <button onClick={onMarkAllAsRead} className="mark-all-btn">
              Mark All as Read
            </button>
          )}
        </div>

        {notifications.length === 0 ? (
          <div className="empty-card">
            <Bell className="empty-icon" size={64} />
            <p className="empty-text">No notifications yet</p>
            <p className="empty-subtext">
              You'll see updates about orders, deliveries, and new artworks here
            </p>
          </div>
        ) : (
          <>
            <div className="tabs">
              <button
                className={`tab ${activeTab === "all" ? "active" : ""}`}
                onClick={() => setActiveTab("all")}
              >
                All ({notifications.length})
              </button>
              <button
                className={`tab ${activeTab === "orders" ? "active" : ""}`}
                onClick={() => setActiveTab("orders")}
              >
                Orders ({orderNotifications.length})
              </button>
              <button
                className={`tab ${activeTab === "artworks" ? "active" : ""}`}
                onClick={() => setActiveTab("artworks")}
              >
                Artworks ({artNotifications.length})
              </button>
            </div>

            <div className="tab-content">
              {getFilteredNotifications().length > 0 ? (
                getFilteredNotifications().map((n) => (
                  <NotificationCard key={n.id} notification={n} />
                ))
              ) : (
                <p className="empty-tab-text">
                  No{" "}
                  {activeTab === "orders"
                    ? "order"
                    : activeTab === "artworks"
                    ? "artwork"
                    : ""}
                  notifications
                </p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
