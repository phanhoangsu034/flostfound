import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaHome, FaInfoCircle, FaBookOpen, FaUser, FaKey, FaSignOutAlt, FaCaretDown } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
    const location = useLocation();
    const { user, logout } = useAuth();
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [activePopup, setActivePopup] = useState(null); // 'about' | 'guide' | null

    const isActive = (path) => {
        return location.pathname === path ? "text-primary font-bold" : "text-gray-600 hover:text-primary";
    };

    const handleMouseEnter = (name) => {
        setActivePopup(name);
        setDropdownOpen(false);
    };

    const handleMouseLeave = () => {
        setActivePopup(null);
    };

    return (
        <nav className="bg-white shadow-md relative z-50">
            <div className="container mx-auto px-4">
                <div className="flex justify-between items-center py-4">
                    <Link to="/" className="text-xl font-bold text-primary flex items-center gap-2">
                        Lost & Found
                    </Link>
                    <div className="flex items-center space-x-6">
                        <Link to="/" className={`flex items-center gap-1 ${isActive('/')}`}>
                            <FaHome /> Trang chủ
                        </Link>

                        {/* About Popup */}
                        <div
                            className="relative py-2" // Added padding-y to help bridge gap if any
                            onMouseEnter={() => handleMouseEnter('about')}
                            onMouseLeave={handleMouseLeave}
                        >
                            <button
                                className={`flex items-center gap-1 focus:outline-none ${isActive('/about')}`}
                            >
                                <FaInfoCircle /> Giới thiệu
                            </button>
                            {activePopup === 'about' && (
                                <div className="absolute top-full left-1/2 -translate-x-1/2 w-64 bg-white border border-gray-200 rounded-xl shadow-xl p-4 animate-fade-in z-50">
                                    <h3 className="font-bold text-gray-800 mb-2">Về CLB Lost & Found</h3>
                                    <p className="text-sm text-gray-600 mb-3">
                                        Nơi kết nối mọi người để tìm lại đồ thất lạc và trao trả cho người mất.
                                    </p>
                                    <Link
                                        to="/about"
                                        className="block text-center bg-primary text-white py-2 rounded-lg text-sm hover:bg-blue-600 transition"
                                        onClick={() => setActivePopup(null)}
                                    >
                                        Xem chi tiết
                                    </Link>
                                </div>
                            )}
                        </div>

                        {/* Guide Popup */}
                        <div
                            className="relative py-2"
                            onMouseEnter={() => handleMouseEnter('guide')}
                            onMouseLeave={handleMouseLeave}
                        >
                            <button
                                className={`flex items-center gap-1 focus:outline-none ${isActive('/guide')}`}
                            >
                                <FaBookOpen /> Hướng dẫn
                            </button>
                            {activePopup === 'guide' && (
                                <div className="absolute top-full left-1/2 -translate-x-1/2 w-64 bg-white border border-gray-200 rounded-xl shadow-xl p-4 animate-fade-in z-50">
                                    <h3 className="font-bold text-gray-800 mb-2">Hướng dẫn sử dụng</h3>
                                    <p className="text-sm text-gray-600 mb-3">
                                        Tìm hiểu cách đăng tin tìm đồ, báo nhặt được đồ và quản lý tài khoản.
                                    </p>
                                    <Link
                                        to="/guide"
                                        className="block text-center bg-primary text-white py-2 rounded-lg text-sm hover:bg-blue-600 transition"
                                        onClick={() => setActivePopup(null)}
                                    >
                                        Xem hướng dẫn
                                    </Link>
                                </div>
                            )}
                        </div>

                        {/* User Dropdown */}
                        {user ? (
                            <div
                                className="relative py-2" // Added padding for hover bridge
                                onMouseEnter={() => {
                                    setDropdownOpen(true);
                                    setActivePopup(null);
                                }}
                                onMouseLeave={() => setDropdownOpen(false)}
                            >
                                <button
                                    className="flex items-center gap-2 focus:outline-none hover:bg-gray-100 px-3 py-2 rounded-lg transition"
                                >
                                    <img
                                        src={user.avatar || "https://via.placeholder.com/30"}
                                        alt="Avatar"
                                        className="w-8 h-8 rounded-full border border-gray-300 object-cover"
                                    />
                                    <span className="font-semibold text-gray-800">{user.name}</span>
                                    <FaCaretDown className="text-gray-500" />
                                </button>

                                {dropdownOpen && (
                                    <div className="absolute right-0 top-full w-56 bg-white border border-gray-200 rounded-lg shadow-xl overflow-hidden animate-fade-in">

                                        <Link
                                            to="/profile"
                                            className="block px-4 py-3 text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                                            onClick={() => setDropdownOpen(false)}
                                        >
                                            <FaUser className="text-primary" /> Hồ sơ cá nhân
                                        </Link>
                                        <Link
                                            to="/change-password"
                                            className="block px-4 py-3 text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                                            onClick={() => setDropdownOpen(false)}
                                        >
                                            <FaKey className="text-yellow-500" /> Đổi mật khẩu
                                        </Link>
                                        <div className="border-t border-gray-100"></div>
                                        <button
                                            onClick={() => {
                                                logout();
                                                setDropdownOpen(false);
                                            }}
                                            className="block w-full text-left px-4 py-3 text-red-600 hover:bg-red-50 flex items-center gap-2"
                                        >
                                            <FaSignOutAlt /> Đăng xuất
                                        </button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <Link to="/profile" className={`flex items-center gap-1 ${isActive('/profile')}`}>
                                <FaUser /> Hồ sơ
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
