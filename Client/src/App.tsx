import "./App.css";
import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./authentication/Login";
import HeatMapPage from "./heatmap/HeatMapPage";
import Dashboard from "./dashboard/Dashboard";
import InventoryManagement from "./dashboard/InventoryManagement";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/heatmap" element={<HeatMapPage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/inventory" element={<InventoryManagement />} />
    </Routes>
  );
}

export default App;
