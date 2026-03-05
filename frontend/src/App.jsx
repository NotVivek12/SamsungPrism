import React from "react";
import { Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext";
import Homepage from "./components/Homepage";
import Statistics from "./components/Statistics";
import Dashboard from "./pages/Dashboard";
import ResearchDashboard from "./components/ResearchDashboard";

export default function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/statistics" element={<Statistics />} />
        <Route path="/faculty-search" element={<Dashboard />} />
        <Route path="/research-insights" element={<ResearchDashboard />} />
      </Routes>
    </ThemeProvider>
  );
}