# 🚀 F-LostFound - Nền tảng tìm đồ thất lạc FPT

Chào mừng bạn gia nhập đội ngũ phát triển dự án F-LostFound. Đây là hệ thống hỗ trợ sinh viên FPT tìm kiếm đồ thất lạc, tích hợp công nghệ AI để nhận diện bài đăng trùng lặp/spam.

## 🛠 1. Yêu cầu hệ thống (Prerequisites)
Trước khi bắt đầu, hãy đảm bảo máy bạn đã có:
- **Python 3.9+** (Khuyên dùng Python 3.11+)
- **Git**
- **Trình duyệt web** (Chrome, Edge, Firefox...)
- Một IDE tùy chọn (Khuyên dùng VS Code)

## 📥 2. Cài đặt dự án (Setup)

**Bước 1: Clone mã nguồn**
Mở Terminal/Command Prompt và chạy:
```bash
git clone https://github.com/phanhoangsu/CTV-Team-1X-BET-23-1.git
cd CTV-Team-1X-BET-23-1
```

**Bước 2: Tạo môi trường ảo (Khuyên dùng)**
Việc này giúp tránh xung đột thư viện giữa các project.
Đứng tại thư mục `CTV-Team-1X-BET-23-1`, chạy:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
*(Nếu kích hoạt thành công, bạn sẽ thấy chữ `(venv)` hiện ở đầu dòng Terminal).*

**Bước 3: Cài đặt các thư viện cần thiết**
Dự án sử dụng Flask, các thư viện AI (scikit-learn) và Cloudinary. Chạy lệnh sau:
```bash
cd backend
pip install -r requirements.txt
```
*(Lưu ý: Bắt buộc phải cd vào thư mục `backend` trước khi thực thi lệnh pip install).*

**Bước 4: Cấu hình môi trường (Environment)**
1. Đảm bảo bạn đang ở thư mục `backend`, hãy tìm file `.env.example`.
2. Tạo một file mới tên là `.env` (ngang hàng với file example) và copy nội dung sang.
3. Điền `SECRET_KEY` (có thể là một chuỗi ký tự ngẫu nhiên bất kỳ để bảo mật session).
4. **Đặc biệt lưu ý:** Bổ sung biến môi trường Cloudinary. Tính năng đăng ảnh bài viết bắt buộc phải có thông số này. (Đăng ký tài khoản miễn phí tại trang chủ Cloudinary để lấy key api):
```ini
CLOUDINARY_URL=cloudinary://943732253697764:kifj9uG7v0mydXq_zJV3H_B_Je4@dbpqjnu0o
```

## 🗄️ 3. Khởi tạo Cơ sở dữ liệu (Database)

Dự án sử dụng **SQLite** làm mặc định ở môi trường phát triển (Development). Do đó, bạn không cần cài đặt SQL Server hay PostgreSQL phức tạp để bắt đầu chạy thử.
Hệ thống sẽ tự động tạo cấu trúc toàn bộ Table và file database là `flostfound.db` nằm ở trong thư mục `backend/instance/` ngay trong lần đầu tiên bạn khởi chạy hệ thống.

**Tuỳ chọn cho ai muốn xài PostgreSQL:**
Nếu nhóm quyết định dùng Postgres cho môi trường dev, vui lòng tham khảo riêng file `backend/LOCAL_DEVELOPMENT.md` để setup chuỗi kết nối bằng biến `DATABASE_URL`.


## 🚀 4. Chạy ứng dụng
Đảm bảo bạn đang ở thư mục gốc của script là `backend` và môi trường ảo `venv` vẫn đang kích hoạt. Khởi chạy ứng dụng:
```bash
python run.py
```
Khi Terminal hiện thông báo: `Running on http://127.0.0.1:5000` (đôi khi là dòng báo của Gunicorn), lúc này hệ thống đã lên! Hãy mở trình duyệt và truy cập địa chỉ đó để bắt đầu sử dụng.


## 👑 5. Phân quyền Admin (Tuỳ chọn)
Để có đặc quyền Admin duyệt bài đăng hoặc quản lý người dùng, bạn cần tự cấp quyền cho chính mình:
1. **Chạy ứng dụng** ở Bước 4 thành công.
2. Mở trình duyệt, vào trang web đăng ký 1 acc mới bình thường.
3. Mở một **Terminal mới** (nhớ kích hoạt lại `venv` và `cd backend`).
4. Chạy script cấp quyền quản trị:
```bash
python scripts/promote_admin.py
```

## 📂 6. Cấu trúc thư mục (Dành cho Dev)
Để không làm rối code của nhau (tránh Conflict), hãy lưu ý quy tắc tổ chức thư mục của project:
- `backend/app/auth/`: Xử lý Đăng ký/Đăng nhập (Authentication).
- `backend/app/posts/`: Quản lý logic bài đăng tìm đồ/trả đồ (View, Create, Update, Delete).
- `backend/app/messages/`: Hệ thống Chat Real-time inbox giữa các user (SocketIO).
- `backend/app/admin/`: Module xử lý Trang Dashboard, duyệt bài, Logs Audit ghi log hành vi.
- `backend/app/services/`: Nơi chứa logic Models AI (Huấn luyện và nhận diện Spam detection bài đăng rác).
- `backend/app/models/`: Cấu trúc Schema các Table trong Database.
- `frontend/templates/`: Chứa các file giao diện đồ hoạ HTML (viết dưới dạng thẻ Jinja2).
- `frontend/static/`: Chứa tệp tĩnh như file cấu hình CSS, JS và hình ảnh cục bộ.


## 🤝 7. Quy trình làm việc (Git Workflow)
Quy tắc vận hành code đẩy lên Github (hạn chế vỡ code người khác):
1. Nhớ luôn gõ **`git pull origin main`** trước khi bắt đầu tạo hay sửa code mới để đồng bộ hóa mã nguồn.
2. Thiết lập nhánh code (Branch) riêng cho mỗi tính năng bạn làm: **`git checkout -b feature/ten-cua-ban`**.
3. Sau khi code xong, thực hiện tuần tự: `git add .` -> `git commit -m "Báo cáo update nội dung gì..."` -> `git push origin feature/ten-cua-ban`.
4. Trở lại GitHub web trên trình duyệt và tạo Pull Request (PR) để chờ Leader và các anh em test chéo. (Tuyệt đối không push thẳng code lên nhánh `main`).

**📌 Sau này khi pull code về:**
Đảm bảo thực hiện các bước này (để mới có key upload img lên cloudinary được do cập nhật):
- **B1:** Vào anti - terminal
- **B2:** `git pull origin master`
- **B3:** `copy .env.example .env`
- **B4:** `python run.py`

## 💡 8. Giải thích các tính năng quan trọng

### 1. Nhắn tin liên hệ trực tiếp
Hệ thống cho phép người dùng click vào nút "Nhắn tin trao đổi" trên bài viết. Thao tác này sẽ tự động mở ra một hộp thoại chat riêng tư trực tiếp với người đã đăng tin. (Lưu ý: Nếu bị kẹt cổng 5000 làm SocketIO không chạy được, hãy kill process đang dùng port 5000 rồi chạy lại `python run.py`).

### 2. Xử lý Thời gian thực (Timezone)
Toàn bộ thời gian hiển thị trên ứng dụng đã được tự động chuẩn hóa. Khi đăng tin, thời gian trên server lưu ở dạng chuẩn UTC và sẽ được tự động dịch sang múi giờ tương ứng (hiện đúng thời gian) trên máy tính/điện thoại người dùng khi họ lướt báo.

### 3. Trạng thái tin đăng (Status)
Hệ thống dùng Trạng thái tin (Status) để báo cáo tiến độ tìm/trả đồ:

- **Chưa giải quyết (Open):** Là trạng thái mặc định lúc vừa đăng xong. Tin này sẽ được tự động hiển thị công khai ở Trang chủ và hệ thống tìm kiếm.
- **Đã giải quyết / Đã hoàn trả (Closed):** Trường hợp đồ thất lạc đã về lại với chủ. Người đăng bài có thể đánh dấu bài viết của họ thành "Đã trả lại/ Đã giải quyết" bằng cách vào **Hồ sơ của tôi -> Tin đã đăng -> Edit**. Khi chuyển sang trạng thái này, bài viết sẽ lập tức ẩn đi khỏi bảng tin Trang chủ để nhường chỗ cho đồ bị mất của người khác đi tìm, nhưng vẫn có thể xem lại nếu dùng bộ lọc tìm kiếm tuỳ chỉnh.


## 🆘 Hỗ trợ
Nếu quá trình cài đặt gặp lỗi xuất hiện trên Terminal báo đỏ (đặc biệt các dạng lỗi `ImportError` ở thư viện scikit-learn, psycopg binary hoặc cài thiếu package eventlet / SocketIO), bạn hãy copy đoạn text log lỗi đó vào box chat team hoặc hỏi ChatBot để được hỗ trợ lệnh pip cài bổ sung ngay kịp thời!

**Chúc bạn có những trải nghiệm code thật tốt và lấy điểm cao cùng đồng đội CTV Team! 🚩**
