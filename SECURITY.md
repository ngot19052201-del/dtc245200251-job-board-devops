# CHÍNH SÁCH BẢO MẬT VÀ CÁC BIỆN PHÁP HARDENING HỆ THỐNG
**Đề tài:** Đề 33 - Website Tuyển dụng / Job Board
**Học phần:** Triển khai và Quản trị Hệ thống Phần mềm
**Sinh viên thực hiện:** TRƯƠNG THỊ BÍCH NGỌC - MSSV: DTC245200251 - Lớp: CNTT-K23C
**Trường:** Đại học Công nghệ Thông tin và Truyền thông - Đại học Thái Nguyên (2026)

---

## 1. TỔNG QUAN VỀ KIẾN TRÚC AN TOÀN THÔNG TIN (SECURITY ARCHITECTURE)

Hệ thống Website Tuyển dụng / Job Board được thiết kế theo nguyên lý **Defense-in-Depth** (Phòng thủ theo chiều sâu) và **Principle of Least Privilege** (Đặc quyền tối thiểu), bao gồm 6 lớp bảo mật cốt lõi:

```
[ Internet / Trình duyệt ]
            │ (Cổng 80/443 HTTPS + Security Headers)
            ▼
┌────────────────────────────────────────────────────────┐
│ 1. LỚP BIÊN (Perimeter): Nginx Reverse Proxy           │
│    - SSL/TLS v1.2/v1.3 Harden Cipher Suites            │
│    - Anti-Clickjacking, Anti-MIME sniffing, XSS block   │
│    - Rate limit & Body size limit (10MB)               │
└───────────────────────────┬────────────────────────────┘
                            │ (frontend-net -> backend-net)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 2. LỚP ỨNG DỤNG: Node.js Express Container             │
│    - Non-root user execution (`USER node`)             │
│    - RBAC Session Auth (Candidate, Recruiter, Admin)   │
│    - File upload validation (MIME + Extension whitelist)│
└───────────────────────────┬────────────────────────────┘
                            │ (backend-net nội bộ)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 3. LỚP CƠ SỞ DỮ LIỆU: MySQL 8.0                        │
│    - Port 3306 Isolated (Không publish ra Host)        │
│    - Non-root database account (`jobuser`)             │
│    - Separate monitoring user (`exporter`)             │
└────────────────────────────────────────────────────────┘
```

---

## 2. CHI TIẾT 6 BIỆN PHÁP BẢO MẬT & HARDENING ĐÃ ÁP DỤNG

### Biện pháp 1: Khởi Chạy Container Dưới Quyền Non-Root (Non-Root Execution)
- **Vấn đề an ninh:** Mặc định container Docker chạy dưới quyền `root` (UID 0). Nếu hacker khai thác được lỗ hổng Remote Code Execution (RCE) trong ứng dụng web, kẻ tấn công có thể thoát container (Container Escape) và chiếm quyền điều khiển toàn bộ máy chủ vật lý/máy ảo host.
- **Giải pháp triển khai:**
  + Trong `app/Dockerfile`, sử dụng tài khoản hệ thống không có quyền root (`USER node`, UID 1000).
  + Thư mục tải lên `/usr/src/app/public/uploads` được phân quyền chính xác thuộc sở hữu của `node:node`.
  + Tích hợp công cụ `dumb-init` làm PID 1 để xử lý đúng các tín hiệu UNIX (`SIGTERM`, `SIGINT`), ngăn chặn zombie process.
- **Cách kiểm chứng:**
  ```bash
  docker exec -it jobboard-webapp whoami
  # Kết quả mong đợi: node (UID 1000, không phải root)
  ```

---

### Biện pháp 2: Phân Tách Mạng Độc Lập (Docker Network Isolation)
- **Vấn đề an ninh:** Nếu tất cả container cùng nằm chung trong một dải mạng phẳng (flat network), một container bị xâm nhập (như Grafana hoặc phpMyAdmin) có thể tự do quét cổng, tấn công leo thang sang cơ sở dữ liệu và các dịch vụ khác (Lateral Movement).
- **Giải pháp triển khai:**
  + Thiết lập 3 mạng bridge cô lập hoàn toàn:
    1. `frontend-net`: Chỉ kết nối giữa Nginx và người dùng ngoài.
    2. `backend-net`: Kết nối Nginx, Node.js Web App, MySQL và phpMyAdmin.
    3. `monitoring-net`: Kết nối Nginx, Prometheus, Grafana, Loki, Promtail, cAdvisor và Exporter.
  + phpMyAdmin và người dùng ngoài không thể truy cập trực tiếp vào dải mạng monitoring hoặc dải mạng hệ điều hành.
- **Cách kiểm chứng:**
  ```bash
  docker network inspect jobboard-frontend-net
  docker network inspect jobboard-backend-net
  docker network inspect jobboard-monitoring-net
  ```

---

### Biện pháp 3: Cách Ly Hoàn Toàn Cổng MySQL (Port 3306 Isolated) & Phân Quyền Non-Root DB
- **Vấn đề an ninh:** Mở cổng MySQL 3306 ra ngoài Internet khiến cơ sở dữ liệu trở thành mục tiêu tấn công hàng đầu của các cuộc tấn công dò quét cổng (Port Scanning), Brute Force mật khẩu root và khai thác lỗ hổng Zero-day.
- **Giải pháp triển khai:**
  + Trong `docker-compose.yml`, dịch vụ `mysql` **tuyệt đối không khai báo directives `ports:`**, cổng 3306 chỉ tồn tại cục bộ trong `backend-net` và `monitoring-net`.
  + Ứng dụng web Node.js kết nối qua tài khoản phân quyền hạn chế `jobuser` (chỉ có quyền trên schema `jobboard_db.*`), tuyệt đối không dùng tài khoản `root`.
  + Dịch vụ giám sát `mysqld-exporter` sử dụng tài khoản riêng `exporter` chỉ có quyền đọc metrics (`PROCESS, REPLICATION CLIENT, SELECT`) và bị giới hạn tối đa 3 kết nối đồng thời.
- **Cách kiểm chứng:**
  ```bash
  netstat -tuln | grep 3306
  # Hoặc:
  ss -tuln | grep 3306
  # Kết quả mong đợi: Không có tiến trình nào lắng nghe cổng 3306 trên Host.
  ```

---

### Biện pháp 4: Quản Trị Bí Mật Qua Biến Môi Trường (.env & .env.example)
- **Vấn đề an ninh:** Hardcode mật khẩu cơ sở dữ liệu, Session Secret hoặc API Keys trực tiếp trong mã nguồn dẫn tới nguy cơ lộ lọt nghiêm trọng khi đưa lên GitHub công khai.
- **Giải pháp triển khai:**
  + Toàn bộ thông tin nhạy cảm (`MYSQL_ROOT_PASSWORD`, `DB_PASSWORD`, `SESSION_SECRET`) được tách biệt vào file `.env`.
  + File `.gitignore` đưa các file bí mật vào danh sách loại trừ không commit lên Git.
  + Cung cấp file mẫu `.env.example` với các giá trị placeholder để người triển khai dễ dàng cấu hình môi trường mới an toàn.

---

### Biện pháp 5: Thiết Lập Bộ Security Headers Đầy Đủ Trên Nginx Reverse Proxy
- **Vấn đề an ninh:** Trình duyệt của người dùng có thể bị tấn công bởi Clickjacking (lồng iframe độc hại), MIME type sniffing (đổi kiểu file để thực thi mã nguồn độc) hoặc tấn công Cross-Site Scripting (XSS).
- **Giải pháp triển khai:**
  + Nginx được cấu hình áp dụng nghiêm ngặt các header bảo vệ:
    * `X-Frame-Options: SAMEORIGIN`: Ngăn chặn website bị nhúng vào `<iframe>` từ các tên miền khác, phòng vệ Clickjacking.
    * `X-Content-Type-Options: nosniff`: Yêu cầu trình duyệt tuân thủ chặt chẽ MIME type được máy chủ gửi về, chống MIME sniffing.
    * `X-XSS-Protection: 1; mode=block`: Kích hoạt bộ lọc XSS của trình duyệt và ngừng render trang nếu phát hiện mã độc.
    * `Referrer-Policy: strict-origin-when-cross-origin`: Bảo vệ tính riêng tư của đường dẫn URL khi người dùng chuyển trang.
    * `Content-Security-Policy (CSP)`: Giới hạn nguồn gốc các script, style, font và hình ảnh chỉ từ các domain tin cậy (`self`, `cdn.jsdelivr.net`, `fonts.googleapis.com`).
- **Cách kiểm chứng:**
  ```bash
  curl -k -I https://localhost
  ```

---

### Biện pháp 6: Kiểm Soát Chặt Chẽ Luồng Tải Tệp CV (File Upload Validation)
- **Vấn đề an ninh:** Chức năng nộp CV là bề mặt tấn công nguy hiểm, hacker có thể tải lên các file mã độc như Web Shell (`.php`, `.js`, `.sh`, `.exe`) hoặc tấn công làm tràn đĩa cứng (DoS disk space) với các file dung lượng khổng lồ.
- **Giải pháp triển khai:**
  + Kiểm tra kép cả phần mở rộng (Extension whitelist: `.pdf`, `.doc`, `.docx`) và MIME type hợp lệ (`application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`).
  + Giới hạn kích thước tệp upload tối đa: Nginx giới hạn `client_max_body_size 10M`, Web application giới hạn `5MB`.
  + Tệp sau khi upload được sinh tên ngẫu nhiên với timestamp (`cv-1729...pdf`) nhằm loại bỏ hoàn toàn tấn công ghi đè file hoặc Directory Traversal (`../../`).

---

## 3. CHECKLIST KIỂM THỬ BẢO MẬT HỆ THỐNG

| STT | Biện pháp bảo vệ | Lệnh / Phương pháp kiểm tra | Trạng thái đạt |
|---|---|---|:---:|
| 1 | Non-root Container | `docker exec jobboard-webapp id` | [x] PASSED (uid=1000) |
| 2 | Network Isolation | `docker network inspect jobboard-backend-net` | [x] PASSED (3 nets) |
| 3 | MySQL Port Isolated | `curl -v telnet://127.0.0.1:3306` (Connection refused) | [x] PASSED |
| 4 | Nginx Security Headers | `curl -k -I https://localhost` (Đủ 5 headers) | [x] PASSED |
| 5 | Upload Validation | Thử gửi tệp `.php` / `.sh` -> Bị từ chối | [x] PASSED |
| 6 | SSL/TLS Encryption | `curl -k -v https://localhost` (TLSv1.3 Handshake) | [x] PASSED |
