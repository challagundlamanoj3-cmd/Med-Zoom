import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import api from "../utils/api";
import "./OtpVerification.css";

function OtpVerification() {
    const [otp, setOtp] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    
    // Get user data passed from signup page
    const { username, email, password } = location.state || {};

    // Redirect to signup if no data
    if (!username || !email || !password) {
        navigate("/signup");
        return null;
    }

    const handleVerify = async (e) => {
        e.preventDefault();

        if (otp.length !== 6) {
            window.alert("Please enter a 6-digit OTP");
            return;
        }

        setLoading(true);
        try {
            const response = await axios.post(api.signup, {
                username,
                email,
                password,
                otp
            });

            if (response.status === 201) {
                window.alert("Signup successful! Please login.");
                navigate("/login");
            }
        } catch (err) {
            if (err.response && err.response.data.error) {
                window.alert(err.response.data.error);
            } else if (err.request) {
                // The request was made but no response was received
                window.alert("Network error: Please check your internet connection and ensure the backend service is running.");
            } else {
                // Something happened in setting up the request that triggered an Error
                window.alert("Verification failed: " + err.message);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
    <div className="otp-verification-page">
        <div className="otp-verification-container">
            <h2>Email Verification</h2>
            <p className="otp-info">Enter the 6-digit OTP sent to {email}</p>

            <form onSubmit={handleVerify} className="otp-form">
                <div className="otp-box-group">
                    {[0, 1, 2, 3, 4, 5].map((index) => (
                        <input
                            key={index}
                            type="text"
                            maxLength="1"
                            className="otp-box"
                            onChange={(e) => {
                                const value = e.target.value.replace(/\D/g, "");
                                if (!value) return;

                                // Set OTP correctly
                                const otpArray = otp.split("");
                                otpArray[index] = value;
                                const newOtp = otpArray.join("");
                                setOtp(newOtp);

                                // Auto-move to next box
                                const next = document.getElementById(`otp-${index + 1}`);
                                if (next) next.focus();
                            }}
                            onKeyDown={(e) => {
                                // Move to previous box on Backspace
                                if (e.key === "Backspace" && !e.target.value) {
                                    const prev = document.getElementById(`otp-${index - 1}`);
                                    if (prev) prev.focus();
                                }
                            }}
                            id={`otp-${index}`}
                        />
                    ))}
                </div>

                <button type="submit" disabled={loading}>
                    {loading ? "Verifying..." : "Verify"}
                </button>
            </form>

            <p className="resend-info">
                Didn’t receive the code? <a href="/signup">Go back to Signup</a>
            </p>
        </div>
    </div>
);
}

export default OtpVerification;
