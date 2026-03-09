import React, { useEffect, useState, useRef } from 'react';
import { updateProfile } from '../services/userService';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { FaUser, FaPhone, FaEnvelope, FaCamera, FaHistory, FaEdit, FaTimes, FaSave, FaKey, FaSignOutAlt } from 'react-icons/fa';

const Profile = () => {
    const { user: authUser, updateUser, logout } = useAuth();
    const navigate = useNavigate();
    const [user, setUser] = useState({
        name: '',
        email: '',
        phone: '',
        avatar: '',
    });
    const [activeTab, setActiveTab] = useState('profile'); // 'profile' or 'activity'
    const [loading, setLoading] = useState(true);
    const [originalUser, setOriginalUser] = useState(null); // Backup for cancel functionality
    const fileInputRef = useRef(null);

    useEffect(() => {
        if (authUser) {
            setUser(authUser);
            setOriginalUser(authUser);
            setLoading(false);
        }
    }, [authUser]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setUser({ ...user, [name]: value });
    };

    const handleAvatarClick = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Validate file type/size if needed
            if (file.size > 2 * 1024 * 1024) { // 2MB
                toast.error("Ảnh quá lớn! Vui lòng chọn ảnh < 2MB");
                return;
            }

            const reader = new FileReader();
            reader.onloadend = () => {
                setUser(prev => ({ ...prev, avatar: reader.result }));
            };
            reader.readAsDataURL(file);
        }
    };

    const handleCancel = () => {
        setUser(originalUser);
        toast.info("Đã hủy thay đổi.");
    };

    const handleSave = async (e) => {
        e.preventDefault();
        try {
            const res = await updateProfile(user);
            if (res.success) {
                toast.success(res.message);
                setOriginalUser(user);
                updateUser(user); // Sync with AuthContext
            }
        } catch (error) {
            toast.error(error);
        }
    };

    const handleLogout = () => {
        if (window.confirm("Bạn có chắc chắn muốn đăng xuất?")) {
            logout();
        }
    };

    if (loading) return <div className="text-center mt-10">Đang tải...</div>;

    return (
        <div className="container mx-auto px-4 py-8">
            <ToastContainer autoClose={2000} />

            {/* Increased Container Size */}
            <div className="bg-white max-w-4xl mx-auto rounded-xl shadow-lg overflow-hidden flex flex-col md:flex-row min-h-[500px]">

                {/* Left Sidebar / Tabs */}
                <div className="md:w-1/4 bg-gray-50 border-r border-gray-200 p-6">
                    <div className="flex flex-col items-center mb-8">
                        <div className="relative group cursor-pointer" onClick={handleAvatarClick}>
                            <img
                                src={user.avatar || "https://via.placeholder.com/150"}
                                alt="Avatar"
                                className="w-32 h-32 rounded-full border-4 border-white shadow-lg object-cover group-hover:opacity-80 transition"
                            />
                            <button className="absolute bottom-1 right-1 bg-primary text-white p-2 rounded-full hover:bg-blue-600 shadow-md">
                                <FaCamera size={16} />
                            </button>
                            <input
                                type="file"
                                ref={fileInputRef}
                                className="hidden"
                                accept="image/*"
                                onChange={handleFileChange}
                            />
                        </div>
                        <h3 className="mt-4 font-bold text-gray-800 text-2xl text-center">{user.name}</h3>
                        <p className="text-base text-gray-500">{user.email}</p>
                    </div>

                    <nav className="space-y-3">
                        {/* Profile Tab */}
                        <button
                            onClick={() => setActiveTab('profile')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 font-medium text-sm shadow-sm border border-transparent
                                ${activeTab === 'profile'
                                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md scale-105'
                                    : 'bg-white text-gray-600 hover:bg-blue-50 hover:text-blue-600 hover:shadow hover:border-blue-100'}
                                active:scale-95 active:shadow-inner active:translate-y-0.5
                            `}
                        >
                            <div className={`p-1.5 rounded-md ${activeTab === 'profile' ? 'bg-white/20' : 'bg-gray-100'}`}>
                                <FaUser />
                            </div>
                            Hồ Sơ Cá Nhân
                        </button>

                        {/* Activity Tab */}
                        <button
                            onClick={() => setActiveTab('activity')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 font-medium text-sm shadow-sm border border-transparent
                                ${activeTab === 'activity'
                                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md scale-105'
                                    : 'bg-white text-gray-600 hover:bg-blue-50 hover:text-blue-600 hover:shadow hover:border-blue-100'}
                                active:scale-95 active:shadow-inner active:translate-y-0.5
                            `}
                        >
                            <div className={`p-1.5 rounded-md ${activeTab === 'activity' ? 'bg-white/20' : 'bg-gray-100'}`}>
                                <FaHistory />
                            </div>
                            Hoạt Động
                        </button>

                        {/* Change Password Link */}
                        <button
                            onClick={() => navigate('/change-password')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 font-medium text-sm shadow-sm border border-transparent bg-white text-gray-600 hover:bg-yellow-50 hover:text-yellow-600 hover:shadow hover:border-yellow-100
                                active:scale-95 active:shadow-inner active:translate-y-0.5
                            `}
                        >
                            <div className="p-1.5 rounded-md bg-gray-100 group-hover:bg-yellow-100">
                                <FaKey />
                            </div>
                            Đổi Mật Khẩu
                        </button>

                        {/* Logout Button */}
                        <button
                            onClick={handleLogout}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 font-medium text-sm shadow-sm border border-transparent bg-white text-red-600 hover:bg-red-50 hover:text-red-700 hover:shadow hover:border-red-100
                                active:scale-95 active:shadow-inner active:translate-y-0.5
                            `}
                        >
                            <div className="p-1.5 rounded-md bg-gray-100 group-hover:bg-red-100">
                                <FaSignOutAlt />
                            </div>
                            Đăng Xuất
                        </button>
                    </nav>
                </div>

                {/* Right Content Area */}
                <div className="md:w-3/4 p-8">
                    {activeTab === 'profile' && (
                        <div>
                            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                                <FaEdit className="text-primary" /> Chỉnh Sửa Thông Tin
                            </h2>
                            <form onSubmit={handleSave} className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {/* Name */}
                                    <div>
                                        <label className="block text-gray-700 text-sm font-bold mb-2">Họ và tên</label>
                                        <div className="relative">
                                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                                <FaUser className="text-gray-400" />
                                            </div>
                                            <input
                                                type="text"
                                                name="name"
                                                value={user.name}
                                                onChange={handleChange}
                                                className="w-full pl-10 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition"
                                                placeholder="Nhập họ tên"
                                            />
                                        </div>
                                    </div>

                                    {/* Phone */}
                                    <div>
                                        <label className="block text-gray-700 text-sm font-bold mb-2">Số điện thoại</label>
                                        <div className="relative">
                                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                                <FaPhone className="text-gray-400" />
                                            </div>
                                            <input
                                                type="text"
                                                name="phone"
                                                value={user.phone}
                                                onChange={handleChange}
                                                className="w-full pl-10 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition"
                                                placeholder="Nhập số điện thoại"
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Email (Readonly) */}
                                <div>
                                    <label className="block text-gray-700 text-sm font-bold mb-2">Email</label>
                                    <div className="relative">
                                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                            <FaEnvelope className="text-gray-400" />
                                        </div>
                                        <input
                                            type="email"
                                            name="email"
                                            value={user.email}
                                            disabled
                                            className="w-full pl-10 px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed"
                                        />
                                    </div>
                                </div>

                                {/* Action Buttons */}
                                <div className="flex items-center gap-4 mt-8 pt-6 border-t border-gray-100">
                                    <button
                                        type="submit"
                                        className="flex-1 bg-primary text-white py-2.5 px-4 rounded-lg hover:bg-blue-600 transition duration-300 font-semibold flex items-center justify-center gap-2 shadow-md"
                                    >
                                        <FaSave /> Lưu Thay Đổi
                                    </button>
                                    <button
                                        type="button"
                                        onClick={handleCancel}
                                        className="flex-1 bg-gray-200 text-gray-700 py-2.5 px-4 rounded-lg hover:bg-gray-300 transition duration-300 font-semibold flex items-center justify-center gap-2"
                                    >
                                        <FaTimes /> Hủy
                                    </button>
                                </div>
                            </form>

                            <div className="mt-6 text-right">
                                <a href="/change-password" className="text-sm text-primary hover:underline font-medium">Đổi mật khẩu?</a>
                            </div>
                        </div>
                    )}

                    {activeTab === 'activity' && (
                        <div>
                            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                                <FaHistory className="text-primary" /> Hoạt Động Của Bạn
                            </h2>

                            {/* Mock Activity List */}
                            <div className="space-y-4">
                                <div className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition bg-gray-50">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h4 className="font-bold text-gray-800">Đăng tin tìm đồ: Chìa khóa xe máy</h4>
                                            <p className="text-sm text-gray-500 mt-1">Đã đăng 2 ngày trước</p>
                                        </div>
                                        <span className="bg-yellow-100 text-yellow-800 text-xs font-semibold px-2.5 py-0.5 rounded">Đang tìm</span>
                                    </div>
                                </div>

                                <div className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition bg-gray-50">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h4 className="font-bold text-gray-800">Đăng tin nhặt được: Thẻ sinh viên</h4>
                                            <p className="text-sm text-gray-500 mt-1">Đã đăng 1 tuần trước</p>
                                        </div>
                                        <span className="bg-green-100 text-green-800 text-xs font-semibold px-2.5 py-0.5 rounded">Đã trả lại</span>
                                    </div>
                                </div>

                                <p className="text-center text-gray-500 italic mt-8">Hết danh sách hoạt động.</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Profile;
