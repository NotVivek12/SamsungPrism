import React, { useState } from "react";
import { ThemeProvider } from "./context/ThemeContext";
import Homepage from "./components/Homepage";
import Statistics from "./components/Statistics";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const handleNavigation = (page) => {
    setCurrentPage(page);
  };

  const handleNavigateBack = () => {
    setCurrentPage('home');
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'statistics':
        return <Statistics onNavigateBack={handleNavigateBack} />;
      case 'faculty-search':
        return <Dashboard />;
      case 'home':
      default:
        return <Homepage onNavigate={handleNavigation} />;
    }
  };

  return (
    <ThemeProvider>
      {renderCurrentPage()}
    </ThemeProvider>
  );
}