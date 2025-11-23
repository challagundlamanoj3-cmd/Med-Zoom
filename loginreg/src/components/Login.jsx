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
      // Configure axios to send credentials
      const config = {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json'
        }
      };
      
      const loginRes = await axios.post(
        api.login,
        { username, password },
        config
      );

      if (loginRes.data === "Success") {
        // Small delay to ensure cookie is set
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Use withCredentials to ensure cookies are sent with the request
        const userConfig = {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json'
          }
        };
        
        // Retry mechanism for user fetch
        let userRes;
        let retries = 3;
        while (retries > 0) {
          try {
            userRes = await axios.get(api.getUser, userConfig);
            break;
          } catch (err) {
            if (retries === 1) throw err; // Last retry, let it throw
            await new Promise(resolve => setTimeout(resolve, 500));
            retries--;
          }
        }

        if (userRes.data.user) {
          setIsLoggedIn(true);
          navigate("/home", { state: { user: userRes.data.user } });
        } else {
          alert("Unable to fetch user: User data is null or undefined");
        }
      } else {
        alert("Login failed: Unexpected response from server");
      }
    } catch (err) {
      if (err.response) {
        alert("Login failed: " + (err.response?.data || err.message));
      } else if (err.request) {
        // The request was made but no response was received
        alert("Network error: Please check your internet connection and ensure the backend service is running.");
      } else {
        // Something happened in setting up the request that triggered an Error
        alert("Login error: " + err.message);
      }
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