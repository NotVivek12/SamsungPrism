import { Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </ThemeProvider>
  );
}