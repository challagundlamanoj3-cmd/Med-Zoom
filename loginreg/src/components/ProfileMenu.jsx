import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import "./ProfileMenu.css";

function ProfileMenu({ isLoggedIn, setIsLoggedIn }) {
    const [open, setOpen] = useState(false);
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:3001";
            await axios.post(`${apiBaseUrl}/logout`, {}, { withCredentials: true });

            setIsLoggedIn(false);
            setOpen(false);
            navigate("/login");
        } catch (error) {
            console.error("Error logging out:", error);
            // Still logout on frontend even if backend fails
            setIsLoggedIn(false);
            setOpen(false);
            navigate("/login");
        }
    };

    return (
        <div className="profile-container">

            {/* Show profile icon ONLY if logged in */}
            {isLoggedIn && (
                <img
                    src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                    alt="profile"
                    className="profile-icon"
                    onClick={() => setOpen(!open)}
                />
            )}

            {/* Dropdown Menu */}
            {isLoggedIn && open && (
                <div className="profile-dropdown">

                    <p className="profile-title">My Profile</p>

                    <Link className="profile-link" to="/about">About Me</Link>
                    <Link className="profile-link" to="/change-pin">Change Pin</Link>

                    <button className="logout-btn" onClick={handleLogout}>
                        Logout
                    </button>
                </div>
            )}

            {/* If NOT logged in → show Login and Signup */}
            {!isLoggedIn && (
                <div className="auth-links">
                    <Link className="login-btn" to="/login">Login</Link>
                    <Link className="signup-btn" to="/signup">Sign Up</Link>
                </div>
            )}
        </div>
    );
}

export default ProfileMenu;