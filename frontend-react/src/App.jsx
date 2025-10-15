import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login";
import Dashboard from "./Dashboard";
import Register from "./Register";
import ServiceProviderLogin from "./ServiceProviderLogin";
import ServiceProviderRegister from "./ServiceProviderRegister";
import ServiceProviderDashboard from "./ServiceProviderDashboard";
import Conversation from "./Conversation";

const API = import.meta.env.VITE_API_URL || "http://localhost:5001";


export default function App() {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const savedUser = localStorage.getItem("user");
    const savedAuth = localStorage.getItem("isAuthenticated");
    
    if (savedUser && savedAuth === "true") {
      setUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            isAuthenticated ? 
            (user?.user_type === "ServiceProvider" ? 
              <Navigate to="/service-provider-dashboard" replace /> : 
              <Navigate to="/dashboard" replace />) : 
            <Register />
          } 
        />
        <Route 
          path="/login" 
          element={
            isAuthenticated ? 
            (user?.user_type === "ServiceProvider" ? 
              <Navigate to="/service-provider-dashboard" replace /> : 
              <Navigate to="/dashboard" replace />) : 
            <Login onLogin={handleLogin} />
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            isAuthenticated && user?.user_type !== "ServiceProvider" ? 
            <Dashboard user={user} onLogout={handleLogout} /> : 
            <Navigate to="/login" replace />
          } 
        />
        <Route 
          path="/service-provider-login" 
          element={
            isAuthenticated ? 
            <Navigate to="/service-provider-dashboard" replace /> : 
            <ServiceProviderLogin onLogin={handleLogin} />
          } 
        />
        <Route 
          path="/service-provider-register" 
          element={
            isAuthenticated ? 
            <Navigate to="/service-provider-dashboard" replace /> : 
            <ServiceProviderRegister />
          } 
        />
        <Route 
          path="/service-provider-dashboard" 
          element={
            isAuthenticated && user?.user_type === "ServiceProvider" ? 
            <ServiceProviderDashboard user={user} onLogout={handleLogout} /> : 
            <Navigate to="/service-provider-login" replace />
          } 
        />
        <Route 
          path="/conversation/:requestId" 
          element={
            isAuthenticated ? 
            <Conversation user={user} /> : 
            <Navigate to="/login" replace />
          } 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

