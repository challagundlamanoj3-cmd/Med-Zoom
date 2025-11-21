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
            const response = await axios.post(api.sendOtp, { email });
            if (response.status === 200) {
                window.alert("OTP sent to your email. Please check your inbox.");
                // Navigate to OTP verification page with user data
                navigate("/verify-otp", { 
                    state: { username, email, password } 
                });
            }
        } catch (err) {
            if (err.response && err.response.data.error) {
                window.alert(err.response.data.error);
            } else {
                console.error("Send OTP Error:", err);
                window.alert("Failed to send OTP");
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