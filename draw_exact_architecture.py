#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Draw exact architecture diagram matching user's reference image
Style: Clean black & white / grayscale UML component diagram
Student: Truong Thi Bich Ngoc - DTC245200251 - CNTT-K23C
"""

import math
from PIL import Image, ImageDraw, ImageFont

def draw_component_icon(draw, x, y, w=20, h=14):
    # Main rectangle
    draw.rectangle([x, y, x + w, y + h], outline='#333333', fill='#FFFFFF', width=1)
    # 2 small tabs on left edge
    draw.rectangle([x - 3, y + 2, x + 3, y + 5], outline='#333333', fill='#FFFFFF', width=1)
    draw.rectangle([x - 3, y + 8, x + 3, y + 11], outline='#333333', fill='#FFFFFF', width=1)

def draw_3d_box(draw, x1, y1, x2, y2, depth=10, fill_color='#FFFFFF', outline_color='#222222'):
    # Back / 3D extrusion
    draw.polygon([
        (x1 + depth, y1 - depth),
        (x2 + depth, y1 - depth),
        (x2, y1),
        (x1, y1)
    ], fill='#F1F5F9', outline=outline_color)
    draw.polygon([
        (x2, y1),
        (x2 + depth, y1 - depth),
        (x2 + depth, y2 - depth),
        (x2, y2)
    ], fill='#E2E8F0', outline=outline_color)
    # Front rectangle
    draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=outline_color, width=2)

def draw_cylinder(draw, x1, y1, x2, y2, fill_color='#FFFFFF', outline_color='#222222'):
    # Database cylinder shape
    w = x2 - x1
    h = y2 - y1
    ry = 12 # vertical radius of oval
    
    # Bottom ellipse
    draw.ellipse([x1, y2 - 2 * ry, x2, y2], fill=fill_color, outline=outline_color, width=2)
    # Body rectangle
    draw.rectangle([x1, y1 + ry, x2, y2 - ry], fill=fill_color, outline=fill_color)
    # Side lines
    draw.line([(x1, y1 + ry), (x1, y2 - ry)], fill=outline_color, width=2)
    draw.line([(x2, y1 + ry), (x2, y2 - ry)], fill=outline_color, width=2)
    # Top ellipse
    draw.ellipse([x1, y1, x2, y1 + 2 * ry], fill=fill_color, outline=outline_color, width=2)

def draw_actor(draw, x, y, label="Người dùng", font=None):
    # Stick figure
    r = 10 # head radius
    draw.ellipse([x - r, y - r, x + r, y + r], outline='#222222', fill='#FFFFFF', width=2) # Head
    draw.line([(x, y + r), (x, y + 35)], fill='#222222', width=2) # Torso
    draw.line([(x - 16, y + 18), (x + 16, y + 18)], fill='#222222', width=2) # Arms
    draw.line([(x, y + 35), (x - 14, y + 55)], fill='#222222', width=2) # Left leg
    draw.line([(x, y + 35), (x + 14, y + 55)], fill='#222222', width=2) # Right leg
    if font:
        draw.text((x, y + 68), label, fill='#000000', font=font, anchor='mm')

def draw_arrow(draw, p1, p2, color='#222222', width=2, arrow_size=8):
    x1, y1 = p1
    x2, y2 = p2
    draw.line([p1, p2], fill=color, width=width)
    
    # Calculate arrow head angle
    angle = math.atan2(y2 - y1, x2 - x1)
    angle_offset = math.pi / 6 # 30 degrees
    
    xa = x2 - arrow_size * math.cos(angle - angle_offset)
    ya = y2 - arrow_size * math.sin(angle - angle_offset)
    xb = x2 - arrow_size * math.cos(angle + angle_offset)
    yb = y2 - arrow_size * math.sin(angle + angle_offset)
    
    draw.polygon([(x2, y2), (xa, ya), (xb, yb)], fill=color)

def generate_uml_diagram(output_path):
    width = 1100
    height = 950
    img = Image.new('RGB', (width, height), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_node_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_comp_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        font_comp_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13.5)
    except:
        font_title = font_node_title = font_comp_name = font_comp_bold = font_sub = font_label = ImageFont.load_default()

    # 1. Main Title
    draw.text((width // 2, 40), "Sơ đồ kiến trúc hệ thống Website Tuyển dụng / Job Board", fill='#000000', font=font_title, anchor='mm')

    # 2. Actor: Người dùng (Top Right)
    actor_x = 780
    actor_y = 110
    draw_actor(draw, actor_x, actor_y, "Người dùng", font=font_label)

    # 3. Main Outer Node: Docker Compose (máy chủ Ubuntu)
    outer_x1 = 70
    outer_y1 = 280
    outer_x2 = 1030
    outer_y2 = 880
    draw.rounded_rectangle([outer_x1, outer_y1, outer_x2, outer_y2], radius=6, fill='#FFFFFF', outline='#444444', width=2)
    draw.text((width // 2, outer_y1 + 18), "Docker Compose (máy chủ Ubuntu)", fill='#000000', font=font_node_title, anchor='mm')

    # 4. Left Node: Giám sát và log tập trung
    left_x1 = 100
    left_y1 = 340
    left_x2 = 600
    left_y2 = 850
    draw.rounded_rectangle([left_x1, left_y1, left_x2, left_y2], radius=4, fill='#FFFFFF', outline='#555555', width=2)
    draw.text(((left_x1 + left_x2) // 2, left_y1 + 20), "Giám sát và log tập trung", fill='#000000', font=font_node_title, anchor='mm')

    # Components inside Left Node:
    # 4.1. Grafana (Top)
    g_x1 = 420; g_y1 = 390; g_x2 = 540; g_y2 = 450
    draw.rectangle([g_x1, g_y1, g_x2, g_y2], fill='#F8FAFC', outline='#444444', width=2)
    draw_component_icon(draw, g_x2 - 18, g_y1 + 4)
    draw.text(((g_x1 + g_x2) // 2, (g_y1 + g_y2) // 2), "Grafana", fill='#000000', font=font_comp_name, anchor='mm')

    # 4.2. Loki (Middle Left)
    lk_x1 = 240; lk_y1 = 580; lk_x2 = 330; lk_y2 = 640
    draw.rectangle([lk_x1, lk_y1, lk_x2, lk_y2], fill='#F8FAFC', outline='#444444', width=2)
    draw_component_icon(draw, lk_x2 - 18, lk_y1 + 4)
    draw.text(((lk_x1 + lk_x2) // 2, (lk_y1 + lk_y2) // 2), "Loki", fill='#000000', font=font_comp_name, anchor='mm')

    # 4.3. Prometheus (Middle Right)
    pr_x1 = 410; pr_y1 = 580; pr_x2 = 560; pr_y2 = 640
    draw.rectangle([pr_x1, pr_y1, pr_x2, pr_y2], fill='#F8FAFC', outline='#444444', width=2)
    draw_component_icon(draw, pr_x2 - 18, pr_y1 + 4)
    draw.text(((pr_x1 + pr_x2) // 2, (pr_y1 + pr_y2) // 2), "Prometheus", fill='#000000', font=font_comp_name, anchor='mm')

    # 4.4. Promtail (Bottom Left)
    pt_x1 = 120; pt_y1 = 730; pt_x2 = 330; pt_y2 = 800
    draw.rectangle([pt_x1, pt_y1, pt_x2, pt_y2], fill='#F8FAFC', outline='#444444', width=2)
    draw_component_icon(draw, pt_x2 - 18, pt_y1 + 4)
    draw.text((pt_x1 + 15, pt_y1 + 16), "Promtail", fill='#000000', font=font_comp_name)
    draw.text((pt_x1 + 15, pt_y1 + 40), "(đọc log container)", fill='#333333', font=font_sub)

    # 4.5. Exporters (Bottom Right)
    ex_x1 = 370; ex_y1 = 730; ex_x2 = 580; ex_y2 = 800
    draw.rectangle([ex_x1, ex_y1, ex_x2, ex_y2], fill='#F8FAFC', outline='#444444', width=2)
    draw_component_icon(draw, ex_x2 - 18, ex_y1 + 4)
    draw.text((ex_x1 + 15, ex_y1 + 16), "Exporters", fill='#000000', font=font_comp_name)
    draw.text((ex_x1 + 15, ex_y1 + 40), "(container, web, DB)", fill='#333333', font=font_sub)

    # 5. Right Top 3D Node: Reverse Proxy
    rp_x1 = 640; rp_y1 = 340; rp_x2 = 930; rp_y2 = 475
    draw_3d_box(draw, rp_x1, rp_y1, rp_x2, rp_y2, depth=10)
    draw.text(((rp_x1 + rp_x2) // 2, rp_y1 + 16), "Reverse Proxy", fill='#000000', font=font_node_title, anchor='mm')

    # Component inside Reverse Proxy: Nginx
    nx_x1 = 660; nx_y1 = 385; nx_x2 = 910; nx_y2 = 460
    draw.rectangle([nx_x1, nx_y1, nx_x2, nx_y2], fill='#FFFFFF', outline='#444444', width=2)
    draw_component_icon(draw, nx_x2 - 18, nx_y1 + 4)
    draw.text((nx_x1 + 15, nx_y1 + 14), "Nginx", fill='#000000', font=font_comp_name)
    draw.text((nx_x1 + 15, nx_y1 + 38), "HTTPS + security headers", fill='#333333', font=font_sub)

    # 6. Right Middle 3D Node: Ứng dụng
    app_x1 = 640; app_y1 = 535; app_x2 = 930; app_y2 = 650
    draw_3d_box(draw, app_x1, app_y1, app_x2, app_y2, depth=10)
    draw.text(((app_x1 + app_x2) // 2, app_y1 + 16), "Ứng dụng", fill='#000000', font=font_node_title, anchor='mm')

    # Components inside Ứng dụng:
    # 6.1. Web Node.js
    web_x1 = 660; web_y1 = 575; web_x2 = 780; web_y2 = 635
    draw.rectangle([web_x1, web_y1, web_x2, web_y2], fill='#FFFFFF', outline='#444444', width=2)
    draw_component_icon(draw, web_x2 - 18, web_y1 + 4)
    draw.text(((web_x1 + web_x2) // 2, (web_y1 + web_y2) // 2), "Web Node.js", fill='#000000', font=font_comp_name, anchor='mm')

    # 6.2. phpMyAdmin
    pma_x1 = 800; pma_y1 = 575; pma_x2 = 920; pma_y2 = 635
    draw.rectangle([pma_x1, pma_y1, pma_x2, pma_y2], fill='#FFFFFF', outline='#444444', width=2)
    draw_component_icon(draw, pma_x2 - 18, pma_y1 + 4)
    draw.text(((pma_x1 + pma_x2) // 2, (pma_y1 + pma_y2) // 2), "phpMyAdmin", fill='#000000', font=font_comp_name, anchor='mm')

    # 7. Database Cylinder: MySQL
    db_x1 = 740; db_y1 = 735; db_x2 = 830; db_y2 = 790
    draw_cylinder(draw, db_x1, db_y1, db_x2, db_y2, fill_color='#F8FAFC')
    draw.text(((db_x1 + db_x2) // 2, (db_y1 + db_y2) // 2 + 5), "MySQL", fill='#000000', font=font_comp_bold, anchor='mm')

    # =========================================================================
    # ARROWS & LABELS (MATCHING REFERENCE IMAGE EXACTLY)
    # =========================================================================

    # 1. Người dùng -> Nginx (HTTPS)
    draw_arrow(draw, (actor_x, actor_y + 80), (actor_x, rp_y1 - 10))
    draw.text((actor_x + 12, 230), "HTTPS", fill='#000000', font=font_label)

    # 2. Nginx -> Grafana (proxy)
    draw_arrow(draw, (nx_x1, 420), (g_x2, 420))
    draw.text((580, 400), "proxy", fill='#000000', font=font_label)

    # 3. Nginx -> Web Node.js (/proxy)
    draw_arrow(draw, (770, nx_y2), (730, web_y1))
    draw.text((725, 498), "/proxy", fill='#000000', font=font_label)

    # 4. Nginx -> phpMyAdmin (proxy)
    draw_arrow(draw, (820, nx_y2), (860, pma_y1))
    draw.text((828, 498), "proxy", fill='#000000', font=font_label)

    # 5. Web Node.js -> MySQL (SQL)
    draw_arrow(draw, (720, web_y2), (765, db_y1))
    draw.text((715, 680), "SQL", fill='#000000', font=font_label)

    # 6. phpMyAdmin -> MySQL (SQL)
    draw_arrow(draw, (860, pma_y2), (805, db_y1))
    draw.text((845, 680), "SQL", fill='#000000', font=font_label)

    # 7. Grafana -> Loki (log)
    draw_arrow(draw, (g_x1 + 30, g_y2), (lk_x2 - 10, lk_y1))
    draw.text((365, 505), "log", fill='#000000', font=font_label)

    # 8. Grafana -> Prometheus (metrics)
    draw_arrow(draw, (g_x2 - 50, g_y2), (pr_x1 + 75, pr_y1))
    draw.text((490, 505), "metrics", fill='#000000', font=font_label)

    # 9. Promtail -> Loki (đẩy log)
    draw_arrow(draw, (pt_x1 + 100, pt_y1), (lk_x1 + 45, lk_y2))
    draw.text((250, 680), "/đẩy log", fill='#000000', font=font_label)

    # 10. Exporters -> Prometheus (thu metrics - curved arrow)
    # Curved path from Exporters top to Prometheus bottom
    p_start = (ex_x1 + 60, ex_y1)
    p_end = (pr_x1 + 60, pr_y2)
    # Draw curved arc
    draw.arc([pr_x1 + 20, pr_y2 - 10, ex_x1 + 80, ex_y1 + 40], start=90, end=270, fill='#222222', width=2)
    draw_arrow(draw, (pr_x1 + 50, pr_y2 + 15), (pr_x1 + 50, pr_y2))
    draw.text((ex_x1 - 10, 680), "thu metrics", fill='#000000', font=font_label)

    # Save image
    img.save(output_path, 'PNG', quality=95)
    print(f"[SUCCESS] Exactly formatted UML diagram generated at: {output_path}")

if __name__ == '__main__':
    generate_uml_diagram('/workspace/screenshots/system_architecture.png')
