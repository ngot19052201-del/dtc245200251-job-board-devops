# WEBSITE TUYỂN DỤNG & VIỆC LÀM (JOB BOARD DEVOPS SYSTEM)
### Đề tài 33 - Học phần Triển khai và Quản trị Hệ thống Phần mềm
**Trường:** Đại học Công nghệ Thông tin và Truyền thông - Đại học Thái Nguyên (2026)  
**Khoa:** Công nghệ Thông tin  
**Sinh viên thực hiện:** TRƯƠNG THỊ BÍCH NGỌC  
**Mã số sinh viên (MSSV):** DTC245200251  
**Lớp:** CNTT-K23C  
**Tên Repository:** DTC245200251-job-board-devops  

---

## 1. GIỚI THIỆU HỆ THỐNG
Dự án là nền tảng Cổng Tuyển Dụng và Việc Làm trực tuyến (Job Board) hoàn chỉnh, được xây dựng theo tiêu chuẩn kiến trúc hiện đại, đóng gói toàn diện bằng Docker Compose, bảo mật đa tầng qua Nginx Reverse Proxy (HTTPS SSL, Security Headers) và tích hợp hệ thống giám sát thời gian thực với Prometheus, Grafana, Loki và Promtail.

### Các Chức Năng Chính:
- **Trang chủ:** Hero banner tìm kiếm thông minh, thống kê số liệu tin tuyển dụng theo thời gian thực, danh mục ngành nghề việc làm, danh sách việc làm mới nhất, nhà tuyển dụng tiêu biểu.
- **Tìm kiếm & Chi tiết việc làm:** Bộ lọc đa tiêu chí (ngành nghề, địa điểm, mức lương, hình thức làm việc), phân trang, hiển thị mô tả, yêu cầu, quyền lợi và hạn nộp hồ sơ.
- **Ứng viên (Candidate):** Đăng ký/đăng nhập, cập nhật hồ sơ cá nhân, tải lên tệp CV (PDF/DOCX kiểm tra dung lượng và định dạng), ứng tuyển việc làm trực tiếp và theo dõi lịch sử xét duyệt hồ sơ.
- **Nhà tuyển dụng (Recruiter):** Bảng điều khiển quản trị tin đăng, đăng tin tuyển dụng mới, chỉnh sửa thông tin tin đăng, duyệt danh sách ứng viên nộp CV, tải xem CV ứng viên và cập nhật trạng thái phỏng vấn/trúng tuyển.
- **Quản trị viên (Admin):** Thống kê tổng quan toàn hệ thống (Users, Jobs, Applications), quản lý và khóa/mở tài khoản người dùng, kiểm duyệt xuất bản hoặc từ chối các tin tuyển dụng.
- **phpMyAdmin:** Quản trị trực quan cơ sở dữ liệu MySQL trên cổng 8080.

---

## 2. KIẾN TRÚC HỆ THỐNG & DOCKER NETWORKS

Toàn bộ hệ thống được cô lập thành **3 dải mạng bridge độc lập**:
1. `jobboard-frontend-net`: Nginx Reverse Proxy tiếp nhận traffic người dùng bên ngoài qua cổng 80 (HTTP) và 443 (HTTPS).
2. `jobboard-backend-net`: Mạng kết nối nội bộ giữa Web Application (Node.js Express), Cơ sở dữ liệu MySQL 8.0 và phpMyAdmin.
3. `jobboard-monitoring-net`: Mạng giám sát kết nối Nginx, Prometheus, Grafana, Loki, Promtail, cAdvisor và mysqld-exporter.

### Danh Sách Cổng Truy Cập (Ports Mapping):
| Dịch vụ | Cổng trên Host | Giao thức | Mục đích |
|---|---|:---:|---|
| **Nginx Reverse Proxy** | `80`, `443` | HTTP / HTTPS | Cổng vào chính của ứng dụng Web JobBoard |
| **Grafana Monitoring** | `3000` | HTTP | Bảng điều khiển trực quan hóa Metrics & Logs |
| **phpMyAdmin** | `8080` | HTTP | Giao diện quản trị CSDL trực quan |
| **MySQL 8.0** | *Không mở cổng host* | TCP (Nội bộ) | Bảo vệ cơ sở dữ liệu chống quét cổng ngoài |

---

## 3. TÀI KHOẢN MẪU DEMO HỆ THỐNG

Hệ thống đã được seeder sẵn các tài khoản demo đầy đủ vai trò:

| Vai trò | Email đăng nhập | Mật khẩu | Chức năng chính |
|---|---|---|---|
| **Quản trị viên (Admin)** | `admin@jobboard.vn` | `Admin@2026` | Toàn quyền quản trị hệ thống, khóa/mở user, duyệt tin |
| **Nhà tuyển dụng (FPT)** | `recruiter@fpt.vn` | `Recruiter@2026` | Quản lý tin FPT Software, xem ứng viên, duyệt CV |
| **Nhà tuyển dụng (Viettel)** | `recruiter@viettel.vn` | `Recruiter@2026` | Quản lý tin Viettel Solutions, tuyển dụng kỹ sư |
| **Ứng viên (Ngọc)** | `bichngoc@jobboard.vn` | `Candidate@2026` | Trương Thị Bích Ngọc - Xem CV, ứng tuyển, xem lịch sử |
| **Ứng viên (Nam)** | `namhoang@gmail.com` | `Candidate@2026` | Ứng viên tự do |
| **Grafana Admin** | `admin` | `Admin@2026` | Xem Dashboards Prometheus và Loki LogQL |
| **MySQL App User** | `jobuser` | `JobPass@2026_Secure` | Tài khoản ứng dụng web kết nối CSDL |

---

## 4. HƯỚNG DẪN KHỞI CHẠY & VẬN HÀNH

### Bước 1: Sao chép file cấu hình môi trường
```bash
cp .env.example .env
```

### Bước 2: Khởi động toàn bộ dịch vụ với Docker Compose
```bash
docker compose up -d --build
```

### Bước 3: Kiểm tra trạng thái các container
```bash
docker compose ps
```
Đảm bảo tất cả 10 container đều ở trạng thái `running` hoặc `healthy`:
- `jobboard-nginx`
- `jobboard-webapp`
- `jobboard-mysql`
- `jobboard-phpmyadmin`
- `jobboard-cadvisor`
- `jobboard-mysqld-exporter`
- `jobboard-prometheus`
- `jobboard-grafana`
- `jobboard-loki`
- `jobboard-promtail`

### Bước 4: Truy cập các giao diện
- **Website Job Board (HTTPS):** `https://localhost` (hoặc `http://localhost` sẽ tự động chuyển hướng sang HTTPS).
- **phpMyAdmin:** `http://localhost:8080` (User: `jobuser`, Pass: `JobPass@2026_Secure`).
- **Grafana Dashboard:** `http://localhost:3000` (User: `admin`, Pass: `Admin@2026`).

---

## 5. KIỂM THỬ GIÁM SÁT PROMETHEUS & LOKI

### Các Câu Truy Vấn PromQL Tiêu Biểu:
1. **CPU Container (%):**
   ```promql
   sum(rate(container_cpu_usage_seconds_total{image!=""}[1m])) by (name) * 100
   ```
2. **RAM Memory Container (Bytes):**
   ```promql
   container_memory_usage_bytes{image!=""} / 1024 / 1024
   ```
3. **Số Kết Nối MySQL (Threads Connected):**
   ```promql
   mysql_global_status_threads_connected
   ```
4. **Trạng thái Healthcheck các dịch vụ (UP):**
   ```promql
   up
   ```

### Các Câu Truy Vấn LogQL Tiêu Biểu:
1. **Toàn bộ log truy cập Nginx:**
   ```logql
   {job="nginx"}
   ```
2. **Lọc log lỗi HTTP 5xx hoặc Error:**
   ```logql
   {job="nginx"} |= "error"
   ```
3. **Lọc Exception ứng dụng Web:**
   ```logql
   {job="webapp"} |~ "(ERROR|Exception|Failed)"
   ```
   *(Có thể truy cập `https://localhost/trigger-error` để kích hoạt log 500 kiểm chứng)*.

---

## 6. LỊCH SỬ GIT COMMITS QUY CHUẨN

Dự án tuân thủ quy chuẩn Conventional Commits với 3 commit bắt buộc:
1. `feat(nginx): add reverse proxy and security headers`
2. `feat(monitoring): add prometheus grafana and exporters`
3. `feat(logging): add loki promtail and logql queries`
