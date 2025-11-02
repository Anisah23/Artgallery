import React from 'react';

export default function LoadingSpinner({ size = 'medium', text = 'Loading...' }) {
  const sizeClass = `spinner-${size}`;

  return (
    <div className="loading-container">
      <div className={`loading-spinner ${sizeClass}`}></div>
      {text && <p className="loading-text">{text}</p>}
    </div>
  );
}