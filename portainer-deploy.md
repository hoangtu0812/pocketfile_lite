# Hướng dẫn triển khai APK Manager qua Portainer

Dự án APK Manager đã được thiết lập sẵn file `docker-compose.yml`, giúp việc triển khai qua **Portainer** cực kỳ đơn giản bằng tính năng **Stacks**.

Có hai cách để triển khai bằng Portainer: **Trực tiếp từ web (Web Editor)** và **Pull từ Git Repository**.

---

## Cách 1: Triển khai bằng Web Editor (Khuyên dùng nội bộ)

Cách này phù hợp khi bạn copy trực tiếp mã nguồn hoặc tải repo `.zip` về máy tính/nhánh đang chạy Portainer, hoặc nếu bạn đã Build sẵn Container Image và đẩy lên Docker Hub. Do hiện tại file `docker-compose.yml` có chứa logic tự Build Image của Backend (`build: context: ./backend`), bạn cần upload nguyên cả tập Source Code dự án.

1. Truy cập vào **Portainer UI** -> Chọn Môi trường (Environment) của bạn (ví dụ: `local`).
2. Vào Menu **Stacks** -> Nhấn nút **+ Add stack** ở góc trên cùng bên phải.
3. Đặt **Name** cho stack, ví dụ: `apk-manager`.
4. Trong phần **Build method**, chọn **Upload**.
5. Bạn nén toàn bộ thư mục dự án này đang có (bao gồm thư mục `backend`, `docker-compose.yml`,...) thành một tập tin `.zip` hoặc `.tar.gz` (lưu ý: Loại bỏ `.env` và thư mục `venv/` hoặc rác ra trước khi nén cho nhẹ).
6. Upload file nén lên Portainer.
7. Di chuyển xuống phần **Environment variables**:
   - Nhấn **Add environment variable** để khai báo các thông số cơ bản. Portainer sẽ lấp đầy các biến bảo mật không cần đẩy lên Git.
   - Thêm các biến sau:
     - `DB_USER`: `apk_user` (hoặc tên tuỳ ý)
     - `DB_PASS`: `MatKhauBaoMatCuaBan`
     - `DB_NAME`: `apk_manager`
     - `SECRET_KEY`: `mot-day-chuoi-ngau-nhien-rat-dai-va-bao-mat` 
     - `MAX_UPLOAD_SIZE`: `524288000` (Tính theo Bytes, mặc định là 500MB)
8. Nhấn nút **Deploy the stack** ở dưới cùng.
9. Portainer sẽ giải nén mã nguồn, tự động build Image cho `backend` và chạy Database. Đợi khoảng 2-3 phút, ứng dụng sẽ lên sóng tại cổng `:8000`.

---

## Cách 2: Triển khai liên kết qua GitHub/GitLab (Khuyên dùng)

Portainer có thể móc thẳng vào Repository Git của bạn và tự động Build lại ứng dụng khi có cập nhật, điều này giúp thiết lập quy trình CI/CD đơn giản. Đảm bảo toàn bộ Code dự án này đã được `git push` lên một repo của bạn.

1. Tương tự, vào Menu **Stacks** -> **+ Add stack**.
2. Đặt **Name**: `apk-manager`.
3. Trong phần **Build method**, chọn **Repository**.
4. Khai báo các thiết lập Git:
   - **Repository URL**: Đường dẫn tới repo của bạn (ví dụ: `https://github.com/my-company/apk-manager.git`)
   - **Repository reference**: Điền nhánh bạn muốn chạy, thường là `refs/heads/main` hoặc `refs/heads/master`.
   - **Compose path**: Giữ nguyên `docker-compose.yml`
5. Trong phần **Environment variables**, Khai báo y hệt như _Bước 7 Cách 1_. Đừng đẩy Passwords hay `SECRET_KEY` vào file `docker-compose.yml` trên Git.
6. (Tuỳ chọn) Bật **GitOps updates**: Nếu bật, khi nhánh master có repo commit mới, Portainer sẽ tự tải về và Restart Stack.
7. Nhấn **Deploy the stack**.

> **⚠️ Lưu ý cực kỳ quan trọng về Volumes khi chạy Portainer:**
> Portainer sẽ tự khởi tạo Docker Volumes chung cho cả PostgreSQL (`pg_data`) và Storage lưu file (`apk_storage`). Tuy nhiên, trong môi trường Production bạn nên cân nhắc đổi Volumes Local này thành một thư mục ảo cụ thể (`/opt/data/apk`) trên máy chủ Host để sao lưu dễ hơn.

---

## Cấu Hình Sau Triển Khai (Dùng lệnh bên trong Container)

Bất kể bạn tạo bằng cách nào, trong lần chạy đầu tiên, bạn cần khởi tạo Database Script (nếu có Alembic Migration) và chèn dữ liệu Admin ban đầu.

1. Bấm vào Stack `apk-manager` trong Portainer -> Chuyển sang danh sách **Containers**.
2. Tìm tới Container mang tên `apk_backend` -> Nhấn biểu tượng dấu nhắc lệnh (**>_** / **Exec Console**).
3. Đăng nhập bằng `User: appuser` (hoặc `root`), Command chạy `/bin/sh`.
4. Gõ các lệnh sau để nạp dữ liệu DB:
   ```bash
   # Chạy Migration để cấu hình bảng Table PostgreSQL
   alembic upgrade head
   
   # Sinh tài khoản Admin mặc định
   python seed.py
   ```
5. Đợi chạy xong là hoàn tất. Bây giờ bạn có thể mở web `http://<IP-SERVER>:8000` và đăng nhập bằng tài khoản `admin` / `password123`.
