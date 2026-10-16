#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate High-Quality System Architecture Diagram
Student: Truong Thi Bich Ngoc - DTC245200251 - CNTT-K23C
"""

import os
from PIL import Image, ImageDraw, ImageFont

def generate_diagram(output_path):
    width = 1600
    height = 1100
    img = Image.new('RGB', (width, height), color='#0F172A') # Dark Slate Background
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_group = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_box_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
        font_box_desc = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except:
        font_title = font_sub = font_group = font_box_title = font_box_desc = font_badge = ImageFont.load_default()

    # Draw Header Banner
    draw.rectangle([(0, 0), (width, 100)], fill='#1E293B')
    draw.text((width // 2, 35), "SƠ ĐỒ KIẾN TRÚC TỔNG THỂ HỆ THỐNG JOB BOARD DEVOPS", fill='#F8FAFC', font=font_title, anchor='mm')
    draw.text((width // 2, 75), "Đề tài 33 - Sinh viên: TRƯƠNG THỊ BÍCH NGỌC | MSSV: DTC245200251 | Lớp: CNTT-K23C (2026)", fill='#38BDF8', font=font_sub, anchor='mm')

    # 1. CLIENT LAYER (Top)
    draw.rounded_rectangle([(100, 130), (1500, 200)], radius=12, fill='#1E293B', outline='#475569', width=2)
    draw.text((width // 2, 150), "LỚP NGƯỜI DÙNG & TRÌNH DUYỆT (INTERNET CLIENTS)", fill='#94A3B8', font=font_group, anchor='mm')
    draw.text((width // 2, 178), "Ứng viên (Candidate)  •  Nhà tuyển dụng (Recruiter)  •  Quản trị viên (Admin)  --->  Truy cập qua HTTPS / HTTP", fill='#F1F5F9', font=font_sub, anchor='mm')

    # Arrow Down from Clients to Nginx
    draw.line([(width // 2, 200), (width // 2, 240)], fill='#38BDF8', width=4)
    draw.polygon([(width // 2 - 8, 235), (width // 2 + 8, 235), (width // 2, 245)], fill='#38BDF8')
    draw.text((width // 2 + 15, 220), "HTTPS :443 (SSL/TLS v1.3) / HTTP :80", fill='#38BDF8', font=font_badge)

    # 2. FRONTEND NETWORK (Gateway Layer)
    draw.rounded_rectangle([(100, 250), (1500, 420)], radius=15, fill='#0B132B', outline='#0284C7', width=3)
    draw.rectangle([(130, 240), (450, 265)], fill='#0284C7')
    draw.text((290, 252), "DẢI MẠNG: jobboard-frontend-net", fill='#FFFFFF', font=font_badge, anchor='mm')

    # Nginx Box
    draw.rounded_rectangle([(140, 280), (1460, 400)], radius=12, fill='#1E293B', outline='#0EA5E9', width=2)
    draw.text((170, 310), "NGINX REVERSE PROXY CONTAINER (jobboard-nginx)", fill='#38BDF8', font=font_box_title)
    draw.text((170, 340), "• Cổng tiếp nhận chính: 80 (HTTP Redirect 301) & 443 (HTTPS)", fill='#E2E8F0', font=font_box_desc)
    draw.text((170, 365), "• Chứng chỉ SSL X.509 RSA 2048-bit (TLSv1.2 & TLSv1.3)", fill='#E2E8F0', font=font_box_desc)
    draw.text((850, 340), "• Security Headers: X-Frame-Options, X-Content-Type-Options, XSS, CSP", fill='#E2E8F0', font=font_box_desc)
    draw.text((850, 365), "• Stub Status Metric Endpoint & Giới hạn upload tệp CV (10MB)", fill='#E2E8F0', font=font_box_desc)

    # 3. BACKEND NETWORK (Left / Middle-Bottom)
    draw.rounded_rectangle([(100, 470), (780, 1040)], radius=15, fill='#0B192C', outline='#10B981', width=3)
    draw.rectangle([(130, 460), (450, 485)], fill='#10B981')
    draw.text((290, 472), "DẢI MẠNG: jobboard-backend-net", fill='#FFFFFF', font=font_badge, anchor='mm')

    # Webapp Box
    draw.rounded_rectangle([(130, 500), (750, 680)], radius=10, fill='#1E293B', outline='#34D399', width=2)
    draw.text((150, 525), "ỨNG DỤNG WEB (jobboard-webapp)", fill='#34D399', font=font_box_title)
    draw.text((150, 560), "• Node.js 20 Express Framework, EJS, Bootstrap 5.3", fill='#E2E8F0', font=font_box_desc)
    draw.text((150, 585), "• Chạy dưới quyền Non-root User (node, UID 1000)", fill='#FCD34D', font=font_box_desc)
    draw.text((150, 610), "• Module: Auth RBAC (Candidate/Recruiter/Admin), Jobs, Upload", fill='#E2E8F0', font=font_box_desc)
    draw.text((150, 635), "• Port nội bộ: 3000 (Không mở ra Host, chỉ Nginx kết nối)", fill='#94A3B8', font=font_box_desc)
    draw.text((150, 658), "• Endpoint giám sát riêng: /metrics & /health", fill='#38BDF8', font=font_box_desc)

    # MySQL Box
    draw.rounded_rectangle([(130, 710), (750, 890)], radius=10, fill='#1E293B', outline='#F59E0B', width=2)
    draw.text((150, 735), "CƠ SỞ DỮ LIỆU MYSQL 8.0 (jobboard-mysql)", fill='#FBBF24', font=font_box_title)
    draw.text((150, 770), "• Database: jobboard_db (6 bảng quan hệ chuẩn hóa 3NF)", fill='#E2E8F0', font=font_box_desc)
    draw.text((150, 795), "• Phân quyền an toàn: User 'jobuser' (KHÔNG dùng root)", fill='#FCD34D', font=font_box_desc)
    draw.text((150, 820), "• CỔNG 3306 ĐƯỢC CÔ LẬP HOÀN TOÀN (Không public Host)", fill='#EF4444', font=font_box_desc)
    draw.text((150, 845), "• Persistent Volume: mysql-data & Tự động chạy seeder", fill='#E2E8F0', font=font_box_desc)
    draw.text((150, 868), "• User riêng cho giám sát: 'exporter' (MAX_CONNECTIONS 3)", fill='#38BDF8', font=font_box_desc)

    # phpMyAdmin Box
    draw.rounded_rectangle([(130, 920), (750, 1010)], radius=10, fill='#1E293B', outline='#64748B', width=2)
    draw.text((150, 945), "QUẢN TRỊ CSDL (jobboard-phpmyadmin)", fill='#E2E8F0', font=font_box_title)
    draw.text((150, 975), "• Public cổng Host: 8080 (Truy cập quản trị CSDL trực quan)", fill='#94A3B8', font=font_box_desc)

    # 4. MONITORING NETWORK (Right / Middle-Bottom)
    draw.rounded_rectangle([(820, 470), (1500, 1040)], radius=15, fill='#18182B', outline='#A855F7', width=3)
    draw.rectangle([(850, 460), (1200, 485)], fill='#A855F7')
    draw.text((1025, 472), "DẢI MẠNG: jobboard-monitoring-net", fill='#FFFFFF', font=font_badge, anchor='mm')

    # Exporters Sub-Box
    draw.rounded_rectangle([(850, 500), (1470, 640)], radius=10, fill='#1E293B', outline='#C084FC', width=2)
    draw.text((870, 525), "BỘ THU THẬP CHỈ SỐ (EXPORTERS TIER)", fill='#C084FC', font=font_box_title)
    draw.text((870, 555), "• cAdvisor (:8080): Giám sát CPU, RAM, Network của 11 containers", fill='#E2E8F0', font=font_box_desc)
    draw.text((870, 580), "• mysqld-exporter (:9104): Thu thập chỉ số hiệu năng MySQL Server", fill='#E2E8F0', font=font_box_desc)
    draw.text((870, 605), "• nginx-prometheus-exporter (:9113): Thu thập metrics stub_status", fill='#E2E8F0', font=font_box_desc)

    # Prometheus Box
    draw.rounded_rectangle([(850, 660), (1470, 780)], radius=10, fill='#1E293B', outline='#F97316', width=2)
    draw.text((870, 685), "PROMETHEUS SERVER (jobboard-prometheus)", fill='#FB923C', font=font_box_title)
    draw.text((870, 715), "• Scrape chu kỳ 10s: 5/5 Targets đều đạt trạng thái UP 100%", fill='#34D399', font=font_box_desc)
    draw.text((870, 740), "• Lưu trữ chuỗi thời gian (TSDB) & Hỗ trợ truy vấn PromQL", fill='#E2E8F0', font=font_box_desc)

    # Grafana Box
    draw.rounded_rectangle([(850, 800), (1470, 910)], radius=10, fill='#1E293B', outline='#F59E0B', width=2)
    draw.text((870, 825), "GRAFANA DASHBOARD (jobboard-grafana)", fill='#FBBF24', font=font_box_title)
    draw.text((870, 855), "• Public cổng Host: 3000 (Đăng nhập: admin / Admin@2026)", fill='#E2E8F0', font=font_box_desc)
    draw.text((870, 880), "• Provisioning tự động: Datasource Prometheus & Loki, Dashboard sẵn", fill='#38BDF8', font=font_box_desc)

    # Loki & Promtail Box
    draw.rounded_rectangle([(850, 930), (1470, 1020)], radius=10, fill='#1E293B', outline='#06B6D4', width=2)
    draw.text((870, 955), "LOKI & PROMTAIL (NHẬT KÝ LOG TẬP TRUNG)", fill='#22D3EE', font=font_box_title)
    draw.text((870, 985), "• Promtail đọc log Nginx & Container Socket  ->  Loki Server (:3100)", fill='#E2E8F0', font=font_box_desc)

    # Inter-network connecting lines
    draw.line([(width // 2, 420), (width // 2, 450)], fill='#64748B', width=3)
    draw.line([(440, 450), (1160, 450)], fill='#64748B', width=3)
    draw.line([(440, 450), (440, 470)], fill='#10B981', width=3)
    draw.line([(1160, 450), (1160, 470)], fill='#A855F7', width=3)

    # Save diagram
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG', quality=95)
    print(f"[SUCCESS] High-res architecture diagram created at: {output_path}")

if __name__ == '__main__':
    generate_diagram('/workspace/screenshots/system_architecture.png')
