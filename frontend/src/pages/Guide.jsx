import React from 'react';

const Guide = () => {
    return (
        <div className="container mx-auto px-4 py-8">
            <div className="bg-white p-8 rounded-lg shadow-md max-w-3xl mx-auto">
                <h1 className="text-3xl font-bold text-primary mb-6">Hướng dẫn sử dụng</h1>

                <div className="space-y-6">
                    <section>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">1. Báo mất đồ</h2>
                        <p className="text-gray-600">
                            Nếu bạn bị mất đồ, hãy vào mục <strong>"Báo mất"</strong> và điền đầy đủ thông tin về món đồ (tên, hình ảnh, đặc điểm, nơi mất).
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">2. Báo nhặt được đồ</h2>
                        <p className="text-gray-600">
                            Nếu bạn nhặt được đồ, hãy đăng tin lên mục <strong>"Nhặt được"</strong> để người mất có thể tìm thấy.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">3. Cập nhật thông tin cá nhân</h2>
                        <p className="text-gray-600">
                            Truy cập <strong>Hồ sơ cá nhân</strong> để cập nhật số điện thoại và đổi mật khẩu để bảo vệ tài khoản.
                        </p>
                    </section>
                </div>
            </div>
        </div>
    );
};

export default Guide;
