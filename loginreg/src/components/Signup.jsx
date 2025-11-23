import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import api, { API_BASE_URL } from "../utils/api";
import "./Signup.css";

function SignUp() {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSendOtp = async (e) => {
        e.preventDefault();
        
        if (!username || !email || !password) {
            window.alert("Please fill in all fields");
            return;
        }
        
        setLoading(true);
        try {
            // Configure axios with proper settings
            const config = {
                timeout: 15000, // 15 second timeout
                withCredentials: true,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            };
            
            // First, check if backend is running
            try {
                console.log("Checking backend health at:", api.health);
                const healthConfig = {
                    timeout: 5000, // 5 second timeout
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                };
                const healthResponse = await axios.get(api.health, healthConfig);
                console.log("Backend is running and healthy:", healthResponse.data);
            } catch (healthErr) {
                console.error("Backend health check failed:", healthErr);
                // Show error to user if health check fails
                if (healthErr.request && !healthErr.response) {
                    const errorMsg = `Backend server is not running or not accessible.\n\n` +
                        `Please ensure:\n` +
                        `1. Backend server is running\n` +
                        `2. Backend URL: ${API_BASE_URL}\n` +
                        `3. No firewall is blocking the connection\n\n` +
                        `To start the backend:\n` +
                        `cd Backend\n` +
                        `python app.py`;
                    window.alert(errorMsg);
                    setLoading(false);
                    return;
                }
                // If it's a different error, log it but continue
                console.warn("Health check failed, but proceeding with OTP request...");
            }
            
            console.log("Sending OTP request to:", api.sendOtp);
            console.log("Request data:", { email });
            
            const response = await axios.post(api.sendOtp, { email }, config);
            
            console.log("OTP response:", response);
            
            if (response.status === 200) {
                window.alert("OTP sent to your email. Please check your inbox.");
                // Navigate to OTP verification page with user data
                navigate("/verify-otp", { 
                    state: { username, email, password } 
                });
            }
        } catch (err) {
            console.error("OTP Error:", err); // For debugging
            console.error("Error details:", {
                message: err.message,
                code: err.code,
                response: err.response,
                request: err.request
            });
            
            if (err.response) {
                // Server responded with error status
                window.alert("Server error: " + (err.response.data.error || err.response.data || "Unknown server error"));
            } else if (err.request) {
                // Request was made but no response received
                const errorMsg = `Network error: Unable to connect to backend server.\n\n` +
                    `Please ensure:\n` +
                    `1. Backend server is running (check Backend folder)\n` +
                    `2. Backend is accessible at: ${api.sendOtp}\n` +
                    `3. No firewall is blocking the connection\n\n` +
                    `To start the backend, run:\n` +
                    `cd Backend\n` +
                    `python app.py`;
                window.alert(errorMsg);
            } else {
                // Something happened in setting up the request
                window.alert("Failed to send OTP: " + err.message);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="signup-page">   {/* <-- fixes centering */}
            <div className="signup-container">  {/* <-- fixes spacing */}
                <h2>Signup</h2>

                <form onSubmit={handleSendOtp}>
                    <input
                        type="text"
                        placeholder="Enter Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />

                    <input
                        type="email"
                        placeholder="Enter Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />

                    <input
                        type="password"
                        placeholder="Enter Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />

                    <button type="submit" disabled={loading}>
                        {loading ? "Sending..." : "Send OTP"}
                    </button>
                </form>

                <p>
                    Already have an account? <Link to="/login">Login</Link>
                </p>
            </div>
        </div>
    );
}

export default SignUp;