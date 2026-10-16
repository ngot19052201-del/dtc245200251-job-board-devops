# TỔNG HỢP CÂU LỆNH TRUY VẤN PROMQL VÀ LOGQL KIỂM CHỨNG HỆ THỐNG
**Đề tài:** Đề 33 - Website Tuyển dụng / Job Board
**Sinh viên thực hiện:** TRƯƠNG THỊ BÍCH NGỌC - MSSV: DTC245200251 - Lớp: CNTT-K23C

---

## 1. CÁC CÂU TRUY VẤN PROMQL (GIÁM SÁT HỆ THỐNG VỚI PROMETHEUS)

### Câu truy vấn 1: Giám sát phần trăm CPU tiêu thụ của từng container theo thời gian thực
```promql
sum(rate(container_cpu_usage_seconds_total{image!=""}[1m])) by (name) * 100
```
- **Ý nghĩa:** Sử dụng hàm `rate()` để tính toán tốc độ tăng của tổng thời gian CPU mà từng container tiêu thụ trong khoảng thời gian cửa sổ trượt 1 phút, sau đó nhân 100 để quy đổi về tỷ lệ phần trăm (%). Giúp phát hiện kịp thời các dịch vụ bị nghẽn tải hoặc tiêu thụ tài nguyên đột biến (như webapp hoặc mysql).

### Câu truy vấn 2: Giám sát dung lượng bộ nhớ RAM (Memory) thực tế mà mỗi container đang chiếm dụng
```promql
container_memory_usage_bytes{image!=""} / 1024 / 1024
```
- **Ý nghĩa:** Đo lường lượng RAM đang sử dụng của từng container (loại trừ các cgroup rỗng không có image) và chia cho 1024^2 để hiển thị theo đơn vị Megabytes (MB). Giúp quản trị viên kiểm soát nguy cơ rò rỉ bộ nhớ (memory leak) hoặc hiện tượng Out-Of-Memory (OOM-Killed) của container.

### Câu truy vấn 3: Giám sát số lượng kết nối đồng thời đang mở tới MySQL Database
```promql
mysql_global_status_threads_connected
```
- **Ý nghĩa:** Thu thập trực tiếp từ `mysqld-exporter` biến trạng thái `Threads_connected` của MySQL Server 8.0. Cho biết số lượng kết nối của các ứng dụng backend hiện đang mở tới database. Nếu con số này tiệm cận ngưỡng `max_connections`, hệ thống sẽ đưa ra cảnh báo nghẽn kết nối.

### Câu truy vấn bổ sung: Kiểm tra trạng thái hoạt động (Healthcheck UP) của toàn bộ scrape targets
```promql
up
```
- **Ý nghĩa:** Trả về giá trị nhị phân `1` nếu target hoạt động bình thường (UP) và `0` nếu target mất kết nối (DOWN).

---

## 2. CÁC CÂU TRUY VẤN LOGQL (TRUY VẤN NHẬT KÝ VỚI LOKI & PROMTAIL)

### Câu truy vấn 1: Xem toàn bộ luồng log truy cập thời gian thực qua Nginx Reverse Proxy
```logql
{job="nginx"}
```
- **Ý nghĩa:** Trích xuất toàn bộ dòng nhật ký (access log và error log) được thu thập từ Nginx container và thư mục `/var/log/nginx/` do Promtail đẩy về Loki server. Giúp theo dõi lưu lượng truy cập của người dùng tới các endpoint của hệ thống.

### Câu truy vấn 2: Lọc các dòng log ghi nhận lỗi mã HTTP 5xx hoặc từ khóa "error" trên Nginx
```logql
{job="nginx"} |= "error"
```
hoặc:
```logql
{job="nginx"} |~ "HTTP/1.[01]\" 5[0-9]{2}"
```
- **Ý nghĩa:** Sử dụng bộ lọc chuỗi `|=` hoặc Regex `|~` để tìm nhanh các yêu cầu gặp sự cố máy chủ nội bộ (500 Internal Server Error, 502 Bad Gateway, 504 Gateway Timeout). Cho phép phát hiện các sự cố gián đoạn dịch vụ tức thì.

### Câu truy vấn 3: Lọc log phát hiện ngoại lệ và lỗi nghiêm trọng trong mã nguồn Web Application
```logql
{job="webapp"} |~ "(?i)(ERROR|Exception|Failed|Uncaught)"
```
- **Ý nghĩa:** Bộ lọc Regex không phân biệt hoa thường `(?i)` tìm kiếm tất cả các thông điệp có chứa từ khóa lỗi như ERROR, Exception, Failed hoặc Uncaught trong container Node.js Express. Giúp đội ngũ DevOps và Developer nhanh chóng truy vết stacktrace lỗi phát sinh trong mã nguồn.
