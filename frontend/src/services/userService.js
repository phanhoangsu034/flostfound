import { userMock } from "../mock/userMock";

const USER_STORAGE_KEY = 'user_profile_data';

// Simulate getting user profile from API (or LocalStorage)
export const getUserProfile = () => {
    return new Promise((resolve) => {
        setTimeout(() => {
            const stored = localStorage.getItem(USER_STORAGE_KEY);
            if (stored) {
                resolve(JSON.parse(stored));
            } else {
                // Init default data if empty
                resolve({ ...userMock });
            }
        }, 500);
    });
};

// Simulate updating user profile
export const updateProfile = (data) => {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            // Validation
            if (!data.name) {
                reject("Tên không được để trống!");
                return;
            }

            // Simple Vietnam phone validation (starts with 0, 10-11 digits)
            const phoneRegex = /^(0)(3[2-9]|5[6|8|9]|7[0|6-9]|8[0-6|8|9]|9[0-4|6-9])[0-9]{7}$/;
            // Or purely generic 10 digits
            const simplePhoneRegex = /^0\d{9}$/;

            if (!data.phone || !simplePhoneRegex.test(data.phone)) {
                reject("Số điện thoại không hợp lệ! (Phải có 10 số, bắt đầu bằng 0)");
                return;
            }

            // Save to persistence
            localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(data));
            console.log("Updated data to backend:", data);
            resolve({ success: true, message: "Cập nhật hồ sơ thành công!" });
        }, 1000);
    });
};
