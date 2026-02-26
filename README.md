# APK Manager — Enterprise

Hệ thống quản lý file APK nội bộ cho doanh nghiệp. Hỗ trợ phân quyền Admin/User, upload/download APK, tree navigation theo Project → Version → File.

---

## 🚀 Quick Start

### Yêu cầu
- Docker & Docker Compose

### 1. Clone & Cấu hình

```bash
cp .env.example .env
# Chỉnh sửa .env nếu cần (đặc biệt SECRET_KEY)
```

### 2. Khởi động

```bash
docker-compose up -d
```

Chờ khoảng 30s để postgres khởi động xong.

### 3. Seed dữ liệu mặc định

```bash
docker-compose exec backend python seed.py
```

### 4. Truy cập ứng dụng

| URL | Mô tả |
|-----|-------|
| http://localhost:8000 | Frontend UI |
| http://localhost:8000/api/docs | Swagger API Docs |

---

## 🔑 Tài khoản mặc định

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `Admin@123` |
| User | `developer` | `Dev@12345` |

---

## 🏗️ Kiến trúc

```
pocketfile/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, Security, Dependencies, Database
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic v2 schemas
│   │   ├── repositories/  # Database access layer
│   │   ├── services/      # Business logic layer
│   │   ├── api/routes/    # FastAPI route handlers
│   │   ├── templates/     # Jinja2 HTML templates
│   │   ├── static/        # CSS & JS
│   │   └── main.py        # App entry point
│   ├── alembic/           # Database migrations
│   ├── seed.py            # Seed data script
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 📡 API Endpoints

### Authentication
```
POST /api/auth/login        # Đăng nhập, trả về JWT token
POST /api/auth/register     # Tạo user mới (admin only)
```

### Projects
```
GET    /api/projects           # Danh sách projects
POST   /api/projects           # Tạo project (admin)
PUT    /api/projects/{id}      # Cập nhật project (admin)
DELETE /api/projects/{id}      # Xoá project (admin)
```

### Versions
```
GET  /api/projects/{id}/versions      # Danh sách versions
POST /api/projects/{id}/versions      # Tạo version (admin)
```

### APK Files
```
POST   /api/versions/{id}/upload        # Upload APK
GET    /api/versions/{id}/files         # Danh sách files
GET    /api/files/{id}/download         # Download APK
DELETE /api/files/{id}                  # Xoá file (admin)
```

### Dashboard
```
GET /api/dashboard/stats    # Thống kê tổng quan
```

**Response format:**
```json
{
  "success": true,
  "data": {},
  "error": null
}
```

---

## 🔧 Migration (Alembic)

```bash
# Tạo migration mới
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migration
docker-compose exec backend alembic upgrade head

# Rollback 1 bước
docker-compose exec backend alembic downgrade -1
```

---

## 🧪 API Testing

### Login và lấy token

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")

echo "Token: $TOKEN"
```

### Tạo project

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"MyApp","description":"My Android Application"}'
```

### Tạo version

```bash
curl -X POST http://localhost:8000/api/projects/1/versions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"version_string":"1.0.0"}'
```

### Upload APK

```bash
curl -X POST http://localhost:8000/api/versions/1/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@app-release.apk"
```

### Dashboard stats

```bash
curl http://localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔒 Security

- JWT authentication (HS256, 24h expiry)
- Password hashing với bcrypt
- Role-based access (ADMIN / USER)
- File paths không expose ra client
- Chỉ cho phép upload `.apk`
- Max upload size configurable

---

## 📦 Environment Variables

| Variable | Default | Mô tả |
|----------|---------|-------|
| `DB_HOST` | postgres | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_USER` | apk_user | Database user |
| `DB_PASS` | apk_pass | Database password |
| `DB_NAME` | apk_manager | Database name |
| `SECRET_KEY` | — | JWT signing key (thay đổi trong production!) |
| `STORAGE_PATH` | /storage | Nơi lưu file APK |
| `MAX_UPLOAD_SIZE` | 524288000 | Max upload (bytes), mặc định 500MB |
| `DEBUG` | false | Debug mode |

---

## 🔮 Extensibility

Kiến trúc được thiết kế để dễ mở rộng:

- **S3 Storage**: Thêm `S3StorageService` implement cùng interface với `StorageService`
- **Audit Logs**: Thêm model `AuditLog` và middleware logging
- **CI/CD Integration**: API endpoints sẵn sàng gọi từ CI pipeline
- **APK Malware Scan**: Plugin vào `APKFileService.upload_apk()`
- **Horizontal Scaling**: Stateless backend, shared storage volume
