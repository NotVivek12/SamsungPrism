import { BrowserRouter as Router,Routes, Route,Navigate} from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext"; // ++ Import the ThemeProvider
import Dashboard from "./pages/Dashboard";
import RequestUpdate from "./layouts/RequestUpdate";
import Ray from "./layouts/Ray";
import WorkletsPage from "./components/WorkletsPage";
import WorkletDetailPage from './components/WorkletDetailsPage';
import Login from "./components/login";

export default function App() {
  return (
    // ++ Wrap your entire application with the ThemeProvider
    <ThemeProvider>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/home" element={<Dashboard />} />
      
        <Route path="/request-update" element={<RequestUpdate/>} />
        <Route path="/ray" element={<Ray />} />
        <Route path="/share-suggestion" element={<Dashboard />} />
        <Route path="/internship-referral" element={<Dashboard />} />
        <Route path="/submit-feedback" element={<Dashboard />} />
        <Route path="/worklets" element={<WorkletsPage />} />
        <Route path="/worklet/:id" element={<WorkletDetailPage />} />
      </Routes>
    </ThemeProvider>
  );
}