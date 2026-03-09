import React from 'react';

const About = () => {
    return (
        <div className="container mx-auto px-4 py-8">
            <div className="bg-white p-8 rounded-lg shadow-md max-w-2xl mx-auto">
                <h1 className="text-3xl font-bold text-primary mb-6">Giới thiệu CLB & Dự án</h1>
                <p className="text-gray-700 leading-relaxed mb-4">
                    Chào mừng đến với website <strong>Tìm Đồ Thất Lạc</strong> của CLB FPTU. Đây là nơi kết nối giữa những người bị mất đồ và những người nhặt được, giúp những món đồ thất lạc sớm tìm được chủ nhân.
                </p>
                <p className="text-gray-700 leading-relaxed mb-4">
                    Dự án được xây dựng với mục tiêu phi lợi nhuận, hỗ trợ cộng đồng sinh viên FPTU.
                </p>
                <div className="mt-6 border-t pt-4">
                    <p className="text-sm text-gray-500">Liên hệ: contact@fptu-club.com</p>
                </div>
            </div>
        </div>
    );
};

export default About;
