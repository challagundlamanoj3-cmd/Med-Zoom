import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import api from "../utils/api";
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
            console.log("[SEND OTP] Attempting to send OTP to:", email);
            console.log("[SEND OTP] API endpoint:", api.sendOtp);
            
            // Configure axios with proper settings
            const config = {
                timeout: 10000, // 10 second timeout
                withCredentials: true,
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            const response = await axios.post(api.sendOtp, { email }, config);
            console.log("[SEND OTP] Response received:", response);
            
            if (response.status === 200) {
                window.alert("OTP sent to your email. Please check your inbox.");
                // Navigate to OTP verification page with user data
                navigate("/verify-otp", { 
                    state: { username, email, password } 
                });
            }
        } catch (err) {
            console.error("[SEND OTP] Error occurred:", err);
            
            if (err.response) {
                // Server responded with error status
                console.error("[SEND OTP] Response error:", err.response.status, err.response.data);
                window.alert("Server error: " + (err.response.data.error || err.response.data || "Unknown server error"));
            } else if (err.request) {
                // Request was made but no response received
                console.error("[SEND OTP] No response received:", err.request);
                window.alert("Network error: Please check your internet connection and ensure the backend service is running at " + api.sendOtp);
            } else {
                // Something happened in setting up the request
                console.error("[SEND OTP] Request setup error:", err.message);
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