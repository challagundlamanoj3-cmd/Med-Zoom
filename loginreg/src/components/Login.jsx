import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import api from "../utils/api";
import "./Login.css";


function Login({ setIsLoggedIn }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      console.log("Attempting login with:", { username, password });
      
      const loginRes = await axios.post(
        api.login,
        { username, password },
        { withCredentials: true }
      );

      console.log("Login response:", loginRes);
      console.log("Login response status:", loginRes.status);
      console.log("Login response data:", loginRes.data);
      console.log("Login response headers:", loginRes.headers);
      
      // Check if the response contains a Set-Cookie header
      if (loginRes.headers['set-cookie']) {
        console.log("Set-Cookie header found:", loginRes.headers['set-cookie']);
      } else {
        console.log("No Set-Cookie header found in login response");
      }

      if (loginRes.data === "Success") {
        console.log("Login successful, attempting to fetch user data...");
        
        // Log document cookies before making the user request
        console.log("Document cookies before user request:", document.cookie);
        
        // Use withCredentials to ensure cookies are sent with the request
        const userRes = await axios.get(
          api.getUser,
          { withCredentials: true }
        );

        console.log("User response:", userRes);
        console.log("User response status:", userRes.status);
        console.log("User response data:", userRes.data);
        console.log("User response headers:", userRes.headers);
        console.log("User data:", userRes.data.user);
        
        // Log document cookies after making the user request
        console.log("Document cookies after user request:", document.cookie);

        if (userRes.data.user) {
          console.log("User data found, setting logged in state and navigating...");
          setIsLoggedIn(true);
          navigate("/home", { state: { user: userRes.data.user } });
        } else {
          console.log("User data is null or undefined:", userRes.data);
          // Let's check what we actually received
          console.log("Full user response data:", JSON.stringify(userRes.data, null, 2));
          alert("Unable to fetch user: User data is null or undefined");
        }
      } else {
        console.log("Login response was not 'Success':", loginRes.data);
        alert("Login failed: Unexpected response from server");
      }
    } catch (err) {
      console.log("Login error:", err);
      console.log("Login error response:", err.response);
      if (err.response) {
        console.log("Error response status:", err.response.status);
        console.log("Error response data:", err.response.data);
        console.log("Error response headers:", err.response.headers);
      }
      alert("Login failed: " + (err.response?.data || err.message));
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h2>Login</h2>

        <form onSubmit={handleLogin}>
          <input 
            type="text" 
            placeholder="Enter Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <input 
            type="password" 
            placeholder="Enter Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)} 
            required
          />

          <button type="submit">Login</button>
        </form>

        <p>
          Don't have an account? <Link to="/signup">SignUp</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;