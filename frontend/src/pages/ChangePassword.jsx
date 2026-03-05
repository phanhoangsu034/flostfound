import React, { useState } from 'react';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { FaLock } from 'react-icons/fa';

const ChangePassword = () => {
    const [formData, setFormData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const { currentPassword, newPassword, confirmPassword } = formData;

        if (!currentPassword || !newPassword || !confirmPassword) {
            toast.error("Vui lòng điền đầy đủ thông tin!");
            return;
        }

        if (newPassword.length < 6) {
            toast.warning("Mật khẩu mới phải từ 6 ký tự trở lên!");
            return;
        }

        if (newPassword !== confirmPassword) {
            toast.error("Mật khẩu mới không trùng khớp!");
            return;
        }

        // Mock success
        setTimeout(() => {
            toast.success("Đổi mật khẩu thành công!");
            setFormData({
                currentPassword: '',
                newPassword: '',
                confirmPassword: ''
            });
        }, 1000);
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <ToastContainer autoClose={2000} />
            <div className="bg-white max-w-md mx-auto rounded-lg shadow-lg p-6">
                <div className="flex justify-center mb-6">
                    <div className="bg-primary p-4 rounded-full">
                        <FaLock className="text-white text-2xl" />
                    </div>
                </div>
                <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Đổi Mật Khẩu</h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-gray-700 text-sm font-bold mb-2">Mật khẩu hiện tại</label>
                        <input
                            type="password"
                            name="currentPassword"
                            value={formData.currentPassword}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="*************"
                        />
                    </div>

                    <div>
                        <label className="block text-gray-700 text-sm font-bold mb-2">Mật khẩu mới</label>
                        <input
                            type="password"
                            name="newPassword"
                            value={formData.newPassword}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="Ít nhất 6 ký tự"
                        />
                    </div>

                    <div>
                        <label className="block text-gray-700 text-sm font-bold mb-2">Xác nhận mật khẩu</label>
                        <input
                            type="password"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="Nhập lại mật khẩu mới"
                        />
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-primary text-white py-2 px-4 rounded-md hover:bg-blue-600 transition duration-300 font-semibold mt-4"
                    >
                        Xác Nhận
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChangePassword;
