import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import api from "../utils/api";
import "./Home.css";

function Home() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true; // Flag to prevent state updates after component unmount
    
    const fetchUserData = async () => {
      try {
        // Add a timeout to prevent indefinite loading
        const timeout = 10000; // 10 seconds
        
        const response = await Promise.race([
          axios.get(api.getUser, { withCredentials: true }),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Request timeout')), timeout)
          )
        ]);
        
        if (!isMounted) return;
        
        if (!response.data.user) {
          // User not authenticated
          navigate("/login");
        } else {
          setLoading(false);
        }
      } catch (error) {
        if (!isMounted) return;
        
        setError(error.message || "Failed to load user data");
        setLoading(false);
        
        // Redirect to login on error
        navigate("/login");
      }
    };
    
    fetchUserData();
    
    // Cleanup function to set isMounted to false when component unmounts
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="home-container">
        <p>Loading...</p>
        {error && <p className="error-message">Error: {error}</p>
}
      </div>
    );
  }

  return (
    <div className="home-container">
      <h2>Welcome to the Home Page!</h2>
      <p>You are successfully logged in.</p>
      {error && <p className="error-message">Note: {error}</p>}
    </div>
  );
}

export default Home;