import React from "react";
import ProfileMenu from "./ProfileMenu";
import "./Navbar.css";

export const Navbar = ({ isLoggedIn, setIsLoggedIn }) => {

    return (
        <nav className="navbar">
            <h2 className="navbar-title">MED ZOOM-AI</h2>

            <div className="navbar-right">
                <ProfileMenu
                    isLoggedIn={isLoggedIn}
                    setIsLoggedIn={setIsLoggedIn}
                />
            </div>
        </nav>
    );
};
