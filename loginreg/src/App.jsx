import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";

import Home from "./components/Home.jsx";
import Login from "./components/Login.jsx";
import SignUp from "./components/Signup.jsx";
import OtpVerification from "./components/OtpVerification.jsx";
import { Navbar } from "./components/NavBar.jsx";   // your new navbar
// import ProtectedRoute from "./Components/ProtectedRoute";  // optional

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check if user already logged in (cookie/session)
  useEffect(() => {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:3001";
    axios.get(`${apiBaseUrl}/user`, { withCredentials: true })
      .then(response => {
        if (response.data.user) {
          setIsLoggedIn(true);
        } else {
          setIsLoggedIn(false);
        }
      })
      .catch(() => setIsLoggedIn(false));
  }, []);

  return (
    <BrowserRouter>

      {/* Always show Navbar at top */}
      <Navbar 
        isLoggedIn={isLoggedIn} 
        setIsLoggedIn={setIsLoggedIn} 
      />

      {/* Push content down so navbar does not hide it */}
      <div style={{ marginTop: "80px" }}>
        <Routes>

          {/* Home Page */}
          <Route path="/home" element={<Home />} />

          {/* Login Page */}
          <Route 
            path="/login"
            element={
              isLoggedIn 
                ? <Navigate to="/home" /> 
                : <Login setIsLoggedIn={setIsLoggedIn} />
            }
          />

          {/* Signup Page */}
          <Route 
            path="/signup"
            element={
              isLoggedIn 
                ? <Navigate to="/home" /> 
                : <SignUp />
            }
          />

          {/* OTP Verification Page */}
          <Route 
            path="/verify-otp"
            element={<OtpVerification />}
          />

          {/* Default Route */}
          <Route path="*" element={<Navigate to="/home" />} />
        </Routes>
      </div>

    </BrowserRouter>
  );
}

export default App;