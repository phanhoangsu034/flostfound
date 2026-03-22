# 🚀 F-LostFound - Nền tảng tìm đồ thất lạc FPT

Chào mừng bạn gia nhập đội ngũ phát triển dự án F-LostFound. Đây là hệ thống web toàn diện (Full-Stack) hỗ trợ cộng đồng sinh viên FPT tìm kiếm đồ đạc và thiết bị thất lạc, được trang bị hệ thống nhắn tin Real-time và gọi điện WebRTC thời gian thực, nổi bật với hệ thống AI tự động phân duyệt bài đăng rác.

## 🌟 Công nghệ sử dụng (Tech Stack)
Hệ thống F-LostFound là một dự án ứng dụng đa dạng những công nghệ hiện đại bậc nhất, giúp sinh viên làm quen trực tiếp với môi trường thực tế (bạn có thể bấm vào link gốc của công nghệ để đọc thêm Docs):

**1. Hệ thống Backend (Server-side):**
- **[Python 3 & Flask Framework](https://flask.palletsprojects.com/):** Nền tảng lõi điều phối kiến trúc Web, đảm bảo tốc độ và độ nhẹ.
- **[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) & [Flask-Login](https://flask-login.readthedocs.io/):** Hệ thống ORM quản lý và tương tác trực tiếp với Database (SQLite/PostgreSQL) bằng Model Objects, hỗ trợ xác thực bảo mật tài khoản.
- **[Flask-SocketIO](https://flask-socketio.readthedocs.io/) & [Eventlet](https://eventlet.net/):** Máy chủ WebSocket xử lý kết nối trực tiếp đa luồng (Concurrency), phân phối tin nhắn inbox và thông báo Real-time mà không cần tải lại trang.
- **[Scikit-learn (AI/ML)](https://scikit-learn.org/):** Module tích hợp Trí tuệ nhân tạo (Học máy ML) đi sâu vào hệ thống để tự động nhận diện và chặn các bài đăng nội dung trùng lặp/Rác/Spam.

**2. Hệ thống Frontend (Client-side):**
- **[Tailwind CSS (v3)](https://tailwindcss.com/):** Framework CSS UI giúp xây dựng nhanh giao diện người dùng Responsive hiện đại, gọn gàng và đồng nhất.
- **[Jinja2 Templating](https://jinja.palletsprojects.com/):** Engine render giao diện HTML tự động từ Server, trộn lẫn Logic vòng lặp Backend một cách mượt mà.
- **[WebRTC API (HTML5)](https://webrtc.org/):** Công nghệ liên lạc kết nối thời gian thực Peer-to-Peer, tự động thu thập luồng Video/Mic qua Web Media API phục vụ chức năng Voice Call/Video Call Đa Nhiệm.
- **[FontAwesome](https://fontawesome.com/):** Bổ sung hệ thống Icon vector độ phân giải sắc nét cho giao diện.

**3. Dịch vụ Đám mây & Triển khai (Cloud & DevOps):**
- **[Cloudinary API](https://cloudinary.com/):** API kết nối Dịch vụ CDN lưu trữ hình ảnh bài viết vĩnh viễn, phân phối tối ưu hoá qua đường truyền siêu tốc.
- **[Metered TURN Server API](https://www.metered.ca/turn-server):** Dịch vụ Relay Server, giúp cuộc gọi Call Video WebRTC "xuyên thủng" qua các tường lửa di động 4G gắt gao.
- **[Railway](https://railway.app/):** Nền tảng hạ tầng tự động hoá (CI/CD Deploy). Fetch nhánh Github lên Deploy sống với Database PostgreSQL mây.

---

## 🛠 1. Yêu cầu hệ thống (Prerequisites)
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

> ⚠️ **LƯU Ý QUAN TRỌNG KHI DEPLOY (LỖI MẤT DỮ LIỆU KHI PUSH GIT)**
> - **Nguyên nhân mất data:** Trên các nền tảng cloud miễn phí như Render hay Railway, hệ thống sử dụng ổ cứng tạm thời (Ephemeral File System). Mỗi lần bạn **Push Code lên Git**, cloud sẽ tự động deploy một bản clone mới, đập bỏ toàn bộ ổ cứng của máy chủ cũ và thiết lập lại từ đầu.
> - **Hậu quả:** Nếu ứng dụng của bạn không kết nối được PostgreSQL mà rơi vào tình trạng chạy dự phòng bằng file `.db` (SQLite) trên server, file đó sẽ bị xoá vĩnh viễn cùng với máy chủ cũ! Trả lại một trang web trắng trơn.
> - **Cách khắc phục:** Trên môi trường Server/Production, **bắt buộc phải sử dụng PostgreSQL** (hoặc hệ CSDL rời) thay vì SQLite. Hãy đảm bảo bạn đã tạo Database PostgreSQL (ví dụ trên Render) và đã thiết lập biến môi trường `DATABASE_URL` chứa chuỗi kết nối chính xác vào cấu hình của Web. Khi đó, dữ liệu của bạn sẽ nằm độc lập và không bao giờ bị mất đi mỗi khi bạn push code cập nhật tính năng mới.

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

### 4. Hệ thống Gọi điện (Voice/Video Call - WebRTC)
Dự án nay đã tích hợp công cụ gọi điện trực tiếp không độ trễ theo chuẩn Zalo/Messenger:
- **Giao diện tiện dụng:** Người dùng có thể nhận cuộc gọi ở định dạng Đổ chuông Toàn cục (Popup rung & Âm thanh) ở bất kỳ trang nào. Có 2 dạng cuộc gọi: Gọi Thoại (Voice) và Gọi Video.
- **Quyền lựa chọn (Receiver's Choice):** Người nhận cuộc gọi Video có toàn quyền quyết định nhấc máy bằng Camera (Hình ảnh 2 chiều) hay nhấc máy bằng Thoại (Tắt camera bản thân để bảo vệ quyền riêng tư).
- **Trải nghiệm Đa nhiệm (Chat song song):** Trong lúc đang gọi điện, người dùng có thể click vào nút **"Thu nhỏ (Minimize)"** để đẩy màn hình cuộc gọi xuống góc màn hình ở dạng luồng nổi (In-App PiP). Giúp linh hoạt tìm kiếm đồ đạc và nhắn tin văn bản đồng thời.
- **Điều khiển trực quan:** Cung cấp Toolbars nâng cao cho phép Tắt Micro cá nhân (Mute), Tắt âm thanh đối phương (Speaker), Bật/Tắt Camera và Nút Cúp Máy. Hiển thị bộ đếm giờ (Timer Counter) tự động chuẩn xác.

**⚙️ Bản Đồ Công Nghệ Lõi Của Hệ Thống Gọi Điện:**
Tính năng Call/Video Call hoạt động dựa trên cơ chế kết nối thời gian thực Peer-to-Peer phức tạp. Dưới đây là các stack công nghệ hiện đại nhất được áp dụng:

*   **[WebRTC API (Web Real-Time Communication)](https://webrtc.org/):** Công nghệ HTML5 tiên tiến nhất hiện nay của W3C. Cho phép hai trình duyệt web trên 2 thiết bị truyền tải trực tiếp luồng Video và Audio (Stream) một cách bảo mật mà không cần nén ném qua Server. Điều này mang lại chất lượng Voice/Video chuẩn HD với chuẩn nén VP8/Opus và độ trễ gần như bằng **0ms**.
*   **[Flask-SocketIO](https://flask-socketio.readthedocs.io/) (Signaling Server):** Được dùng vào vai trò làm "Tổng đài viên bắt tay". Vì 2 trình duyệt không biết nhau ở đâu trên thế giới, Socket.IO sẽ chuyên chở nhanh chóng các gói thông số mạng (Session Description Protocol - SDP `Offers/Answers`) với tốc độ Real-time mili-giây để hai thiết bị nhận diện ra nhau.
*   **[Google Public STUN Servers](https://gist.github.com/yetithefoot/7592580):** Máy chủ khai phá tường lửa độc quyền từ Google (Sử dụng IP: `stun:stun1.l.google.com:19302`). Giúp trình duyệt ở một mạng WiFi nội bộ NAT (như khu nhà trọ, trường học) có thể tự vạch trần raịa chỉ IP Public của chính nó ra mạng Internet toàn cầu.
*   **[Metered TURN Server API](https://www.metered.ca/turn-server):** Nền tảng chuyên dụng cấp phát máy chủ trung chuyển (Relay). Đây là **công nghệ chống màn hình đen**. Khi nhà mạng viễn thông như 4G cấu hình các tường lửa chống vượt quyền ngặt nghèo (Symmetric NAT) ngăn chặn WebRTC P2P gọi trực tiếp, Metered TURN Server sẽ đứng ra làm Node trạm bơm dữ liệu Video để chắc chắn rằng *100% người dùng sẽ gọi được và nghe thấy nhau*.
*   **[TailwindCSS](https://tailwindcss.com/) & Web Media API:** Xử lý cấp quyền Camera/Mic từ phần cứng người dùng (qua hàm `navigator.mediaDevices`) và render giao diện gọi điện thoại đa nhiệm In-App Picture-in-Picture (PiP).

**🔑 Hướng dẫn lấy & Lắp Key API Cấu hình TURN Server:**
Theo mặc định, ứng dụng cần một cổng dịch vụ mở kết nối TURN từ hệ thống Metered. Để dự án hoạt động trơn tru lúc phát hành, các dev trong team cần đăng ký Key API cá nhân miễn phí theo từng bước sau:

**Bước 1: Lấy API Key**
1. Truy cập trang web chính thức: **[Metered.ca TURN Server](https://www.metered.ca/turn-server)**.
2. Bấm **Get Started for Free** để tạo một tài khoản (Gói Free Tier cho sinh viên cho phép sử dụng **50 GB Băng thông / Tháng**, mức chịu tải có thể lên đến hàng trăm cuộc gọi Video cùng lúc).
3. Sau khi xác thực và vào Dashboard điều khiển, tìm đến Menu **TURN Servers > Instructions**.
4. Bạn sẽ thấy một mã định danh dài gọi là `API Key`. Vui lòng **Copy cấu trúc chuỗi API Key** này. Ví dụ: `cc15a353e53bc386edaa8488d5672b82d82e`.

**Bước 2: Nạp API Key vào Source Code (Thực hiện bởi Dev)**
1. Mở file quản lý thiết lập gọi điện trên Frontend: `frontend/templates/messages/webrtc_modals.html`.
2. Dùng công cụ tìm kiếm trong file (Ctrl + F), tìm tên hàm Javascript: `initIceServers()`.
3. Bạn sẽ thấy dòng code gọi (Fetch API REST) như sau:
   ```javascript
   const response = await fetch("https://f-lost-found-call.metered.live/api/v1/turn/credentials?apiKey=API_KEY_CŨ_Ở_ĐÂY");
   ```
4. **Xóa đoạn mã API KEY bị bôi đỏ** ở cuối URL và Dán chèn mã **API Key mới** của bạn vào đúng sau dấu `=`.
5. Hãy lưu file lại (`Ctrl + S`), Mở Terminal chạy lệnh Commit Git: `git commit -m "Update API Key hệ thống TURN Server mới"`. Sau đó Push lên Server chạy Real-time! Toàn bộ tính năng sẽ thông suốt trở lại.

**🔄 Luồng hoạt động (The Flow):**
1. **Khởi tạo:** Người gọi (Caller) ấn click. Trình duyệt truy cập phần cứng Media và tạo ra gói tin `Offer`.
2. **Signaling:** Gói tin `Offer` được mã hoá và quăng lên máy chủ Flask qua SocketIO để chuyển tiếp đích danh tên người nhận.
3. **Đổ chuông (Ringing):** Socket.io ở client người nhận (Receiver) bắt được tín hiệu `Offer`. Lập tức kích hoạt nhạc chuông và hiển thị Modal Nhấc máy, *bất chấp họ đang ở trang nào trên hệ thống* (Global Socket).
4. **Chấp nhận & Trả lời:** Khi Receiver bấm "Nghe", máy nhận khởi tạo Media và tạo gói dữ liệu `Answer` gửi ngược về máy người gọi.
5. **Streaming (P2P Connectivity):** Hai máy trao đổi các `ICE Candidates` để tìm đường mạng tối ưu nhất. Khi tìm thành công, luồng Video/Audio lập tức kết nối trực tiếp với nhau, hoàn tất đàm thoại.

### 5. Hệ thống Khôi phục Mật khẩu (Forgot Password via EmailJS & APIs)

**A. Tính năng & Công nghệ Nổi bật (Tech Stack):**
Hệ thống cấp lại mật khẩu được xây dựng theo chuẩn hiện đại, ưu tiên tuyệt đối trải nghiệm UI/UX và bảo mật:
1. **Frontend (Client-side):**
   - **EmailJS SDK:** Thư viện gửi email Serverless trực tiếp từ trình duyệt mà không cần Backend phải cài đặt Server SMTP tốn kém (Rất phù hợp để làm đồ án).
   - **Vanilla JavaScript (ES6+):** Xử lý DOM Manipulation (bật/tắt hình con mắt soi mật khẩu), dùng Regex Validation để làm hiệu ứng thanh năng lượng (Strength bar) thay đổi màu `Đỏ -> Vàng -> Xanh` theo nhịp gõ, và Validate Real-time giúp tự động viền đỏ báo lỗi khi 2 ô mật khẩu gõ lệch nhau.
     > **C. Cơ chế chấm điểm độ mạnh mật khẩu (Strength Rules):**
     >
     > ✅ CÁCH ĐÚNG (THEO CODE CỦA BẠN)
     > 
     > 🔴 **ĐỎ (Weak)**
     > 👉 Điểm ≤ 2
     > 📌 Nghĩa là: Thiếu nhiều yếu tố bảo mật
     > *Ví dụ:*
     > - `123456` (chỉ có số)
     > - `abcdef` (chỉ chữ thường)
     > 👉 ❗ Không phải chỉ “text” là đỏ — mà là ít tiêu chí
     > 
     > 🟡 **VÀNG (Medium)**
     > 👉 Điểm = 3 hoặc 4
     > 📌 Nghĩa là: Có kết hợp nhiều yếu tố nhưng chưa đủ mạnh
     > *Ví dụ:*
     > - `abc123` (chữ + số)
     > - `Matkhau1` (hoa + thường + số)
     > 
     > 🟢 **XANH (Strong)**
     > 👉 Điểm = 5 (đủ hết)
     > 📌 Phải có:
     > ✔ ≥ 6 ký tự
     > ✔ chữ thường
     > ✔ chữ hoa
     > ✔ số
     > ✔ ký tự đặc biệt
     > 
     > *Ví dụ:* `Admin@123`

   - **Fetch API:** Bắn luồng dữ liệu bất đồng bộ (Async request) lên Backend mà không cần tải lại trang.

2. **Backend (Server-side):**
   - **Flask Blueprint (`auth_password_reset_bp`):** Module API Router độc lập, giúp source code luôn duy trì chuẩn Clean Code, dễ dàng bảo trì.
   - **Mã hóa Token (itsdangerous):** Link gửi về Email chứa Token mã vạch (Hash) tự động hết hạn sau 60 phút. Đặc biệt Token được cấu thành từ `SECRET_KEY` của ứng dụng kết hợp vân tay người dùng nên Hacker rà quét link vô tình cũng không thể tấn công.
   - **Flask-Login (`logout_user`):** Cơ chế Auto Logout cưỡng chế đá văng phiên đăng nhập cũ (Session) ngay sau khi đối tượng cập nhật thành công mật khẩu mới.

**B. Cách dùng & Luồng trải nghiệm (The Flow):**
1. Mở trang chủ ứng dụng, chọn mục **Đăng nhập**. Click vào đường link: `Quên mật khẩu?`.
2. Gõ địa chỉ email của tài khoản đang sở hữu -> Bấm **"Gửi link khôi phục"**.
3. *[Luồng ngẩm]* Frontend sẽ Fetch API xác thực Database Backend -> Nếu tồn tại khớp email, Backend sinh mã Token độc nhất có thời hạn và ném về Frontend -> Frontend thao tác gọi EmailJS móc thẳng Link vừa tạo kèm Tên chủ sở hữu vào một Template Mail đã định dạng và gửi thẳng vào Hộp thư đến người dùng.
4. Mở Gmail (hoặc check thư mục Spam) để nhận Email Khôi phục gửi về tức thì. 
5. Bấm vào thư, click chọn nút lệnh **Đặt lại mật khẩu**.
6. Điền mật khẩu mới với trợ lý ảo soi lỗi tự động trên màn hình -> Click Cập nhật thành công và hệ thống tự quay về màn Login.

**🔑 HƯỚNG DẪN CÁCH LẤY PUBLIC API KEY EMAILJS DÀNH CHO TEAM DEV**
> 🧠 **Nói cho Giám khảo:** “Public API Key được lấy trong phần Account của hệ thống EmailJS và dùng để khởi tạo kết nối (Initialize) ở tầng Frontend khi phát tín hiệu gửi thư điện tử đi ra ngoài hệ thống mạng.”

👉 **Bước 1:** Đăng nhập trang quản lý EmailJS. Cột dọc góc bên trái dưới cùng, chọn **Account**.
👉 **Bước 2:** Chuyển qua tab **General**.
👉 **Bước 3:** Tìm đến box thông số **API keys**. Cẩn thận nhìn 2 dòng mã khác nhau:
   - ✅ `Public Key`: xxxxxxxxxx *(Quyền kết nối Frontend: Được phép Cấp vào mã nguồn).* 
   - ❌ `Private Key`: xxxxxxxxxx *(Dành cho Node Backend: TUYỆT ĐỐI KHÔNG SỬ DỤNG. Lộ key là bị tận dụng hack gửi mail rác)*
👉 **Bước 4:** Copy đoạn mã nội dung của **Public Key** (Ví dụ Public key của nhóm: `FiWoCZgxcRcbBod10`).
👉 **Bước 5 (Triển khai Code):** Vào Source Code của hệ thống tìm đến file `frontend/templates/auth/forgot_password.html`, dán đè dãy mã vừa xong vào dòng quy định cấu hình liên kết ban đầu `emailjs.init("FiWoCZgxcRcbBod10");` -> Kết thúc thành công!

---

### 6. Hệ thống Xác nhận Đăng ký bằng Mã OTP (EmailJS)

Tính năng Đăng ký tài khoản nay đã được tích hợp luồng xác thực rào cản **OTP (One-Time Password)** thông qua EmailJS, giúp hệ thống chống lại tình trạng tạo tài khoản rác (spam accounts) bằng email ảo.

**A. Quy trình hoạt động (The Flow):**

Mô hình luồng dữ liệu diễn ra dưới dạng "Bất đồng bộ" theo thứ tự 7 bước như sau:
**1. Khởi chạy biểu mẫu (Initialize):** Người dùng điền User, Pass, và Email có thật ở form Đăng ký.
**2. Tiền xác thực (Pre-validation):** Ấn *[Gửi Mã Xác Nhận]*, Javascript gọi ngầm Fetch API `POST /api/check_register` dò Database. Trùng Username/Email thì báo đỏ chặn lại, không trùng mới cho đi tiếp -> Cực kỳ tiết kiệm API Call cho EmailJS.
**3. Kiến tạo OTP:** Javascript Frontend khởi chạy thuật toán Random sinh ra đúng 1 chuỗi 6 số ngẫu nhiên.
**4. Phát tín hiệu Email (Dispatch):** SDK `emailjs.send()` lập tức kẹp 6 số OTP nhảy thẳng vào thư người dùng mượt mà mà không làm khựng màn hình.
**5. Chuyển cảnh Trực quan (Transition):** Form đăng ký biến mất, Form giao diện nhập mã OTP hiện ra (Không hề F5 tải lại trang Web).
**6. Verify:** Người dùng nhập 6 số. Gõ bừa thì chửi sai ngay ở giao diện.
**7. Hoàn tất chu kỳ:** Mã khớp 100%, Frontend mới thực sự ra lệnh gửi Form đi. Backend đón lấy Data thông tin User vào bảng SQLite tạo tài khoản và chuyển hướng cái rụp về Login.

---

**B. Cơ chế sinh mã OTP (Giải thích cho Giám khảo):**

🔢 **MỤC TIÊU CỐT LÕI**
👉 Tạo ra 1 số có đúng 6 chữ số (VD: `123456`, `654321`, `908172`). 
💻 Hệ thống sử dụng 1 dòng code duy nhất: `Math.floor(100000 + Math.random() * 900000)`

🧠 **BÓC TÁCH HIỂU TỪNG BƯỚC (RẤT DỄ):**

**1. `Math.random()`**
👉 Lệnh cơ bản của đồ hoạ máy tính. Nó cho ra một số thập phân siêu nhỏ: `0` → `0.999...`

**2. `* 900000` (Nhân mở rộng dải số)**
🎯 **VÌ SAO VẪN CÓ KHẢ NĂNG LỖI (KHÔNG ĐỦ 6 SỐ)?**
👉 Vì sau khi nhân, khoảng thập phân trở thành: `0` → `899999`. 
👉 **KHÔNG PHẢI** toàn bộ hệ thống này đều là số có 6 chữ số. Tách ra cho bạn thấy:
❌ **Số KHÔNG đủ 6 chữ số (Rất nhiều):**
- `0` → `9` *(1 chữ số)*
- `10` → `99` *(2 chữ số)*
- `100` → `999` *(3 chữ số)*
- `1000` → `9999` *(4 chữ số)*
- `10000` → `99999` *(5 chữ số)*
✅ **Số ĐỦ 6 chữ số:** Chỉ từ `100000` → `899999` mới đủ tiêu chuẩn!
👉 **BẢN CHẤT:** `Math.random()` bốc thăm ngẫu nhiên KHẮP toàn bộ khoảng, nên nó hoàn toàn có thể xui xẻo rơi vào vùng nhỏ (số bé ❌) hoặc vùng lớn (số 6 chữ số ✅). Do đó, khoảng từ `0` đến `899999` vẫn chứa nguy cơ phá hỏng form giao diện do hụt số.

**3. `+ 100000` (Phép cộng Bảo Hiểm)**
👉 Cấp bù dời lịch trình lên thêm 10 vạn, dải số biến thành: `100000 → 999999`
🔥 → Ép dải này **LUÔN LUÔN** rớt vào mốc 6 chữ số! Thả tự do bao nhiêu ngàn lần cũng ra đủ 6 chữ số.

**4. `Math.floor()`**
👉 Chặt mẹt phần số lẻ phần thập phân đi ➡️ Trả về một **Số Nguyên Mịn Màng**.

📌 **VÍ DỤ THỰC TẾ:**
- `random()` bốc trúng: `0.5`
- `* 900000` -> `450000`
- `+ 100000` -> `550000`
- `Math.floor()` chặt lẻ -> Kết quả cuối: **`550000`**

💡 **TÓM LẠI: TẠI SAO PHẢI CỘNG +100000?**
👉 Nếu không cộng: Code có thể vớ vẩn nhả ra số `1234` (Email OTP mà 4 số là đứt gánh form sinh viên). ❌
👉 Có cộng vào: Kết quả **luôn ≥ 100000** → Bảo lãnh an toàn 100% ra đủ 6 số! ✅

🧠 **CÂU TRẢ LỜI NGẮN (MANG ĐI THUYẾT TRÌNH BẢO VỆ):**
> *"Dạ nhóm em dùng Toán dời khoảng. Em chạy randomize bốc lấy một số nguyên trong dải bảo hiểm từ 100000 đến 999999. Việc cộng thêm cơ số mười vạn nhằm triệt tiêu hoàn toàn tỷ lệ rủi ro rơi vào các con số ở mốc hàng nghìn, hàng chục nhằm đảm bảo mã OTP bắn vào Email luôn luôn có độ dài tuyệt đối là 6 chữ số ạ!"*

---

### 7. Hệ thống Đăng nhập Nhanh Mạng Xã Hội (Social Login - Google & Facebook)

Tính năng này cho phép người dùng lướt qua rào cản gõ mật khẩu thủ công bằng cách vay mượn danh tính định danh an toàn từ Hệ sinh thái của Google và Meta (Facebook). 

**A. Các Cột Trụ Công Nghệ Bố Trí (Tech Stack):**
1. **Frontend (Bắt tương tác):** 
   - **Firebase Authentication (v9 Modular):** Cầu nối (SDK) hiện đại nhất chuyên trị các giao thức bật cửa sổ Popup trơn tru để giao tiếp với OAuth 2.0 của Google/Facebook mà không làm giật trang.
   - **Vanilla Javascript (ES6) + Fetch API:** Bộ tóm bắt tín hiệu JSON trả về (Email, Tên hiển thị, Avatar) và chuyển lậu xuống Backend dưới nền.
2. **Backend (Python Flask):**
   - **Flask API Router (`/api/social_login`):** Bến cảng đón dữ liệu JSON do Javascript đẩy xuống.
   - **Python `secrets` Module:** Sinh mã Token 16 byte mã hóa sinh nhẫu nhiên phục vụ mục đích "Khoá trái cửa".
   - **Flask-Login (`login_user`):** Ghi dấu ấn (Session cookie) báo hiệu đăng nhập thành công.

**B. Quy trình hoạt động (Luồng Data Flow):**
Toàn bộ quy trình diễn ra chớp nhoáng theo 5 bước dưới đây:

**[Bước 1] Kích hoạt Cổng Dịch vụ (Trigger):**
Tại màn hình `/login`, người dùng từ chối điền form và ấn vào 1 trong 2 nút đăng nhập Google/Facebook.

**[Bước 2] Trình diện Ủy quyền (OAuth 2.0 Consent):**
Javascript gọi lệnh `signInWithPopup(auth, provider)` của Firebase. Một cửa sổ nhỏ độc lập lập tức phi lên màn hình. 
- *Với Google:* Khay chọn Gmail hiện ra cho chọn tài khoản.
- *Với Facebook:* Hộp thoại kiểm duyệt của Meta sẽ kiểm tra trạng thái Token. Nếu qua ải (Đã cấu hình cấp quyền Scopes `email` & `public_profile` tại Developer Portal), hệ thống sẽ gật đầu.

**[Bước 3] Vận chuyển Dữ liệu (Dispatch Data):**
Cửa sổ Popup tự động khép lại. Firebase nhả về rổ dữ liệu tinh khiết gồm: Đầu vào Email `user.email`, Tên định danh `user.displayName` và Ảnh đại diện gốc `user.photoURL`. Frontend bọc tất cả lại thành khối JSON, vác đi Fetch bắn vào Cổng `POST` bên Backend.

**[Bước 4] Hành vi Não Bộ Backend (Database Logic Processing):**
API Backend túm lấy gói JSON và tiến hành xẻ đôi kịch bản kiểm tra:
👉 *Kịch bản A (Tài khoản đã có tiền sự / Người quen):* 
Máy chủ quét Database `User.query.filter_by(email)`. Thấy tồn tại! Nó chỉ việc lôi mã định danh thẻ Session của anh này ra và dập mộc duyệt lệnh truyền lệnh `login_user(user)`.

👉 *Kịch bản B (Lính mới hoàn toàn):* 
Máy chủ lục bảng không thấy Email này. Nó sẽ chơi chiêu Tạo Tài Khoản Nhanh Vô Cực!
- Tự động cắt xén tên Google cấp để khai sinh cho `username` độc quyền (bằng thuật toán vòng lặp cộng dồn nếu vô tình trùng với người khác).
- **Vá lỗ hổng cực gắt:** Vì Login qua bên thứ 3 không cung cấp "Mật khẩu Cứng", Backend sẽ dùng hàm `secrets.token_urlsafe(16)` thả vào 1 cái dãy mật khẩu rác dài dằng dặc, băm nát ra rồi lưu Hash vào ổ đĩa. Mục đích là để cấm tiệt người dùng tìm cách Login bằng giao diện điền Form cổ điển.
- Save Database `commit()` -> Dập mộc duyệt Session người mới.

**[Bước 5] Cú Chốt Trực Quan (Redirect Success):**
Backend báo về con số Status `200 Success`. Ở cổng diện Website Frontend, Javascript đọc thấy liền vác luôn mã lệnh `window.location.href = '/'` ném người dùng rơi thẳng cẳng vào Trang Chủ F-LostFound. Hoàn tất quá trình Login không tốn một lần gõ phím!

**C. Hướng dẫn Cài đặt & Cơ chế Tích hợp (Setup Guide từ A-Z):**

Để triển khai hệ thống Social Login mượt mà lên Đồ án, nhà phát triển cần tuân thủ cấu hình chéo trên 3 nền tảng: **Firebase Console**, **Meta for Developers** và **Mã nguồn Source Code**. Dưới đây là biên bản thao tác chi tiết:

👉 **GIAI ĐOẠN 1: Chuẩn bị "Giấy Phép" tại Firebase**
1. Đăng nhập trang quản trị **Firebase Console** -> Tạo Project mới.
2. Vào thẻ **Authentication** -> Thẻ phụ **Sign-in method**. Bấm `Add new provider`.
3. Bật công tắc **`Enable`** cho 2 Provider là **Google** và **Facebook**.
   - *Riêng với Google:* Bắt buộc phải sổ thanh Dropdown chọn "Project support email" (Email hiển thị của Developer) rồi ấn nút **Save**.

👉 **GIAI ĐOẠN 2: Lấy thông quan Mạng Xã Hội (Facebook Developer)**
1. Mở trang quản lý ứng dụng của Facebook tại `developers.facebook.com`.
2. Tạo 1 App. Vào menu góc trái kiếm chữ **Facebook Login** -> **Settings (Cài đặt)**.
3. Quay ngược lại trang Firebase lúc nãy, bật sửa nút Facebook, kéo xuống tận cùng copy đường dính mã `OAuth redirect URI` (Ví dụ: `https://...firebaseapp.com/__/auth/handler`).
4. Mang đoạn đường dẫn đó Dán thẳng vào ô **"Valid OAuth Redirect URIs"** bên trang thiết lập của Facebook rồi ấn **Save Changes**. 
5. Cuối cùng, vào thẻ **Use cases** (Trường hợp Cấp quyền) -> Ở mục "Xác thực và tạo tài khoản" -> Chỉnh sửa -> Nhấn nút **Add (Thêm)** cấp quyền truy xuất `email` và `public_profile` để chặn lọt rào bảo mật.

👉 **GIAI ĐOẠN 3: Thiết lập rào chắn tại Firebase (Cho phép Tên Miền)**
Mặc định hệ thống OAuth không cho Web trôi nổi ăn cắp Data. Ta phải đăng ký trước những website được phép xài.
1. Ở trang Firebase Authentication -> Chuyển sang thẻ **Settings (Cài đặt)** -> **Authorized domains**.
2. Ấn **Add domain** và nhập mọi đường Link URL bạn chạy web vào đây (Không gõ `https://` và dấu `/` ở cuối).
   - Link chạy Nháp Dưới Máy: `127.0.0.1` 
   - Link chạy Website Production thật sự: `1x-bet.up.railway.app` (Link của Railway).

👉 **GIAI ĐOẠN 4: Thả mã vào Source Code Front-End**
Xong thủ tục hành chính, lập trình viên truy cập file đăng nhập chính (Ví dụ: `login.html`), móc nối SDK của Firebase vào mã HTML theo công thức Javascript v9 Modular:
```javascript
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, FacebookAuthProvider } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Khởi tạo Firebase App từ Bộ Keys (Public) cấp tại Console
const firebaseConfig = { apiKey: "XXX", authDomain: "XXX", ... };
const auth = getAuth(initializeApp(firebaseConfig));

// Nóng súng: JS bật Popup Gọi Xác Thực
signInWithPopup(auth, new GoogleAuthProvider()).then(result => {
    // Trích xuất thành công: result.user.email & result.user.displayName
    // Đóng gói JSON bắn gửi FETCH API về Flask Backend
});
```

---

<!-- ## ⚠️ Giới hạn của Facebook Login - Tại Sao Không Public Được?

### 📌 Vấn đề gặp phải
Tính năng **Đăng nhập bằng Facebook** đã được tích hợp hoàn chỉnh về mặt kỹ thuật (Firebase Auth SDK + Backend API), tuy nhiên **không thể cho toàn bộ người dùng public sử dụng** do chính sách bảo mật của Meta (Facebook).

### 🕵️ Nguyên nhân gốc rễ - Scandal Cambridge Analytica (2018)
Năm 2018, công ty **Cambridge Analytica** đã lợi dụng Facebook Login API để thu thập trái phép dữ liệu của **87 triệu tài khoản Facebook** mà người dùng không hay biết. Dữ liệu này được dùng để lập hồ sơ tâm lý và **can thiệp bầu cử tổng thống Mỹ 2016**. Facebook bị kiện ra tòa và bị **phạt 5 tỷ USD** bởi Ủy ban Thương mại Liên bang Hoa Kỳ (FTC), đồng thời bị Quốc hội Mỹ điều trần.

### 🔒 Hệ quả - Meta siết chặt chính sách App Review
Sau scandal trên, Meta (Facebook) ban hành chính sách bắt buộc **tất cả ứng dụng bên thứ ba** muốn truy cập dữ liệu người dùng (kể cả chỉ Email) **phải trải qua quy trình App Review và xác minh danh tính**:

| Yêu cầu | Mô tả |
|---|---|
| **Xác minh doanh nghiệp** | Phải có pháp nhân công ty hoặc CMND cá nhân |
| **App Review** | Meta duyệt thủ công mục đích sử dụng dữ liệu |
| **Privacy Policy** | Phải có trang chính sách bảo mật công khai |
| **Data Deletion URL** | Phải có endpoint để người dùng xóa dữ liệu |

### 🎓 Ảnh hưởng đến Đồ án Sinh viên
Chính sách này được thiết kế cho **doanh nghiệp có pháp nhân**, không dự tính đến trường hợp sinh viên làm đồ án. Do nhóm không có giấy phép kinh doanh và thời gian xét duyệt của Meta không cố định (1 ngày đến vài tuần), việc Public App Facebook **nằm ngoài tầm kiểm soát của nhóm**.

### ✅ Giải pháp thay thế đã áp dụng
- **Google Login**: Hoạt động hoàn toàn bình thường, không yêu cầu App Review
- **Facebook Login cho Tester**: Có thể add tối đa 50 tài khoản Facebook cụ thể vào danh sách Tester để sử dụng tính năng này trong môi trường Development -->

---

## 🆘 Hỗ trợ
Nếu quá trình cài đặt gặp lỗi xuất hiện trên Terminal báo đỏ (đặc biệt các dạng lỗi `ImportError` ở thư viện scikit-learn, psycopg binary hoặc cài thiếu package eventlet / SocketIO), bạn hãy copy đoạn text log lỗi đó vào box chat team hoặc hỏi ChatBot để được hỗ trợ lệnh pip cài bổ sung ngay kịp thời!

**Chúc bạn có những trải nghiệm code thật tốt và lấy điểm cao cùng đồng đội CTV Team! 🚩**
