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
1. `frontend_net`: Nginx Reverse Proxy tiếp nhận traffic người dùng bên ngoài qua cổng 80 (HTTP) và 443 (HTTPS).
2. `backend_net` (`internal: true`): Mạng kết nối nội bộ cô lập hoàn toàn giữa Web Application (Node.js Express), Cơ sở dữ liệu MySQL 8.0, phpMyAdmin và mysqld-exporter. Container MySQL chỉ nằm duy nhất trong mạng này và không mở cổng 3306 ra ngoài Host.
3. `monitoring_net`: Mạng giám sát kết nối Nginx, Prometheus, Grafana, Loki, Promtail, cAdvisor và các Exporter.

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

### Cách 1: Khởi chạy toàn bộ hệ thống bằng Docker Compose (Khuyên dùng)

#### Bước 1: Chuẩn bị tệp cấu hình môi trường
```bash
cp .env.example .env
```
*(Nếu cần, có thể mở file `.env` để tùy chỉnh mật khẩu hoặc cổng dịch vụ)*.

#### Bước 2: Khởi động toàn bộ dịch vụ
```bash
docker compose up -d --build
```
> **Lưu ý:** Lần đầu khởi chạy, Docker sẽ build image cho Web App và Nginx, đồng thời tự động nạp cơ sở dữ liệu mẫu từ thư mục `mysql-init/`.

#### Bước 3: Kiểm tra trạng thái các container
```bash
docker compose ps
```
Đảm bảo tất cả **11 container** đều ở trạng thái `running` hoặc `healthy`:
1. `jobboard-nginx` - Cổng vào Reverse Proxy (cổng 80, 443)
2. `jobboard-webapp` - Ứng dụng Node.js Express (cổng 3000 nội bộ)
3. `jobboard-mysql` - Cơ sở dữ liệu MySQL 8.0 (cô lập nội bộ)
4. `jobboard-phpmyadmin` - Giao diện quản trị CSDL trực quan (cổng 8080)
5. `jobboard-cadvisor` - Thu thập metrics container (cổng 8080 nội bộ)
6. `jobboard-mysqld-exporter` - Xuất metrics MySQL sang Prometheus
7. `jobboard-nginx-exporter` - Xuất metrics Nginx sang Prometheus
8. `jobboard-prometheus` - Máy chủ giám sát và lưu trữ số liệu
9. `jobboard-grafana` - Dashboard trực quan hóa số liệu và log (cổng 3000)
10. `jobboard-loki` - Thu thập và lưu trữ log tập trung
11. `jobboard-promtail` - Đẩy log Nginx và Docker lên Loki

#### Bước 4: Truy cập các giao diện dịch vụ

> 📌 **Xác định địa chỉ IP máy ảo (nếu truy cập từ máy thật Windows / macOS):**
> Chạy lệnh sau trên terminal Ubuntu để lấy địa chỉ IP:
> ```bash
> hostname -I | awk '{print $1}'
> ```
> *(Ví dụ IP nhận được: `192.168.181.128`)*

##### Bảng Địa Chỉ Truy Cập Chi Tiết:

| Dịch vụ | URL từ Trình duyệt trong máy ảo (VM) | URL từ Trình duyệt máy thật (Host Windows/Mac) | Tài khoản mặc định | Ghi chú |
|---|---|---|---|---|
| **Cổng Tuyển Dụng (HTTPS)** | `https://localhost` | `https://<IP_MÁY_ẢO>` *(VD: `https://192.168.181.128`)* | Xem bảng tài khoản ở Mục 3 | Nhấn **Advanced -> Proceed** khi trình duyệt báo SSL tự ký |
| **Cổng HTTP (Tự động redirect)** | `http://localhost` | `http://<IP_MÁY_ẢO>` *(VD: `http://192.168.181.128`)* | - | Nginx tự động chuyển hướng 301 sang HTTPS |
| **Quản trị phpMyAdmin** | `http://localhost:8080` | `http://<IP_MÁY_ẢO>:8080` | `jobuser` / `JobPass@2026_Secure` | Quản trị bảng, dữ liệu ứng viên & việc làm |
| **Bảng điều khiển Grafana** | `http://localhost:3000` | `http://<IP_MÁY_ẢO>:3000` | `admin` / `Admin@2026` | Xem Dashboard giám sát hệ thống & Logs |

> ⚠️ **HƯỚNG DẪN XỬ LÝ CẢNH BÁO SSL TRÊN TRÌNH DUYỆT (BẮT BUỘC ĐỌC):**
> 
> Khi truy cập vào `https://localhost` hoặc `https://<IP_MÁY_ẢO>`, các trình duyệt hiện đại (Chrome, Edge, Firefox, Brave...) sẽ xuất hiện màn hình cảnh báo màu đỏ: *"Kết nối của bạn không phải là kết nối riêng tư / Your connection is not private"* (mã lỗi `NET::ERR_CERT_AUTHORITY_INVALID` hoặc `NET::ERR_CERT_COMMON_NAME_INVALID`).
> 
> **Đây là cơ chế bảo mật tiêu chuẩn khi dùng chứng chỉ SSL tự ký (Self-signed Certificate) trong môi trường phát triển/thực nghiệm, KHÔNG PHẢI lỗi hệ thống.**
> 
> **Cách xử lý để vào trang web:**
> 1. **Cách 1 (Phổ biến):** Nhấp vào nút **Nâng cao (Advanced)** ở góc dưới -> chọn **Tiếp tục truy cập ... (không an toàn) / Proceed to ... (unsafe)**.
> 2. **Cách 2 (Mẹo nhanh cho Chrome / Edge):** Nếu trình duyệt không hiển thị nút tiếp tục, bạn chỉ cần nhấp chuột vào khoảng trống bất kỳ trên trang cảnh báo và gõ trực tiếp chữ:
>    ```text
>    thisisunsafe
>    ```
>    *(Trình duyệt sẽ tự động mở trang web ngay lập tức).*
> 3. **Trên Firefox:** Nhấp **Nâng cao (Advanced)** -> chọn **Chấp nhận rủi ro và tiếp tục (Accept the Risk and Continue)**.

> ℹ️ **Lưu ý về Cổng kết nối (Ports Mapping):**
> - Website Tuyển Dụng chạy qua **Nginx Reverse Proxy** tại cổng **80 (HTTP)** và **443 (HTTPS)**. Node.js backend (`jobboard-webapp`) được bảo vệ hoàn toàn trong Docker network nội bộ và không mở cổng 3000 ra host.
> - Cổng **`:3000`** trên Host được dành riêng cho **Grafana Monitoring Dashboard**.
> - Cổng **`:8080`** trên Host được dành cho **phpMyAdmin**.

---

### Các Lệnh Quản Trị & Vận Hành Tiêu Biểu:

- **Xem log thời gian thực của toàn bộ hệ thống:**
  ```bash
  docker compose logs -f
  ```
- **Xem log riêng của ứng dụng Web hoặc Nginx:**
  ```bash
  docker compose logs -f webapp
  docker compose logs -f nginx
  ```
- **Tạm dừng các container (không xóa dữ liệu):**
  ```bash
  docker compose stop
  ```
- **Khởi động lại các container:**
  ```bash
  docker compose start
  ```
- **Tắt và xóa các container:**
  ```bash
  docker compose down
  ```
- **Reset toàn bộ hệ thống & xóa dữ liệu database để nạp lại từ đầu:**
  ```bash
  docker compose down -v
  docker compose up -d --build
  ```

---

### Cách 2: Khởi chạy ứng dụng Web độc lập (Local Development không Docker)

Nếu muốn phát triển hoặc kiểm thử trực tiếp mã nguồn Node.js:
1. Đảm bảo MySQL đang chạy và đã import file [01_schema.sql](file:///home/ubuntu/dtc245200251-job-board-devops/mysql-init/01_schema.sql) và [02_seed_data.sql](file:///home/ubuntu/dtc245200251-job-board-devops/mysql-init/02_seed_data.sql).
2. Di chuyển vào thư mục ứng dụng và cài đặt dependencies:
   ```bash
   cd app
   npm install
   ```
3. Cấu hình tệp `app/.env` trỏ đúng thông tin kết nối MySQL (host: `localhost`).
4. Chạy ứng dụng:
   ```bash
   npm start
   ```
5. Mở trình duyệt tại: `http://localhost:3000`.

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
