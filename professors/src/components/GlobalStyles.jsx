import React, { useEffect } from 'react';

// This component adds custom global styles to the application
const GlobalStyles = () => {
  useEffect(() => {
    // Insert CSS for grid cards that need max-height setup
    const styleEl = document.createElement('style');
    styleEl.textContent = `
      /* Set max-height for card content */
      .card-content-scrollable {
        max-height: 300px;
        overflow-y: auto;
      }
      
      /* Custom scrollbar styling */
      .card-content-scrollable::-webkit-scrollbar {
        width: 4px;
      }
      .card-content-scrollable::-webkit-scrollbar-track {
        background: #f1f5f9;
      }
      .card-content-scrollable::-webkit-scrollbar-thumb {
        background-color: #cbd5e1;
        border-radius: 20px;
      }
      .dark .card-content-scrollable::-webkit-scrollbar-track {
        background: #1e293b;
      }
      .dark .card-content-scrollable::-webkit-scrollbar-thumb {
        background-color: #475569;
      }
    `;
    document.head.appendChild(styleEl);
    
    return () => {
      document.head.removeChild(styleEl);
    };
  }, []);
  
  return null;
};

export default GlobalStyles;