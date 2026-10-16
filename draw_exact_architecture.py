#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
High-Resolution System Architecture Diagram Generator
Topic: Job Board DevOps System (De tai 33)
Matches the exact structure, layout, and style of reference image with razor-sharp typography.
Outputs both:
  1. screenshots/system_architecture.png (Ultra-crisp 300 DPI raster)
  2. screenshots/system_architecture.svg (Scalable vector graphic)
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

def draw_component_icon(draw, x, y, w=32, h=20, outline_color='#333333', stroke_w=2):
    """Draw standard UML 2.0 component icon (box with 2 protruding tabs on left)"""
    # Main rectangle body
    draw.rectangle([x, y, x + w, y + h], outline=outline_color, fill='#FFFFFF', width=stroke_w)
    # 2 small protruding tabs on the left border
    tab_w = 7
    tab_h = 4
    draw.rectangle([x - 4, y + 3, x + 3, y + 3 + tab_h], outline=outline_color, fill='#FFFFFF', width=stroke_w)
    draw.rectangle([x - 4, y + 11, x + 3, y + 11 + tab_h], outline=outline_color, fill='#FFFFFF', width=stroke_w)

def draw_3d_box(draw, x1, y1, x2, y2, depth_x=22, depth_y=22, fill_color='#FFFFFF', outline_color='#222222', stroke_w=3):
    """Draw UML deployment node 3D isometric box"""
    # Top face
    draw.polygon([
        (x1, y1),
        (x1 + depth_x, y1 - depth_y),
        (x2 + depth_x, y1 - depth_y),
        (x2, y1)
    ], fill='#FAFAFA', outline=outline_color)
    
    # Right face
    draw.polygon([
        (x2, y1),
        (x2 + depth_x, y1 - depth_y),
        (x2 + depth_x, y2 - depth_y),
        (x2, y2)
    ], fill='#F0F2F5', outline=outline_color)

    # Front main rectangle
    draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=outline_color, width=stroke_w)
    
    # Redraw crisp 3D outline strokes
    draw.line([(x1, y1), (x1 + depth_x, y1 - depth_y)], fill=outline_color, width=stroke_w)
    draw.line([(x1 + depth_x, y1 - depth_y), (x2 + depth_x, y1 - depth_y)], fill=outline_color, width=stroke_w)
    draw.line([(x2 + depth_x, y1 - depth_y), (x2, y1)], fill=outline_color, width=stroke_w)
    draw.line([(x2 + depth_x, y1 - depth_y), (x2 + depth_x, y2 - depth_y)], fill=outline_color, width=stroke_w)
    draw.line([(x2 + depth_x, y2 - depth_y), (x2, y2)], fill=outline_color, width=stroke_w)

def draw_cylinder(draw, x1, y1, x2, y2, fill_color='#FFFFFF', outline_color='#222222', stroke_w=3):
    """Draw 3D database cylinder with smooth bottom curve and no middle chord line"""
    ry = 22  # Vertical radius of top/bottom ellipse
    
    # Fill bottom body with polygon
    pts = [(x1, y1 + ry), (x2, y1 + ry), (x2, y2 - ry)]
    for deg in range(0, 181, 10):
        rad = math.radians(deg)
        cx = (x1 + x2) / 2.0
        cy = y2 - ry
        rx = (x2 - x1) / 2.0
        px = cx + rx * math.cos(rad)
        py = cy + ry * math.sin(rad)
        pts.append((px, py))
    pts.append((x1, y2 - ry))
    draw.polygon(pts, fill=fill_color)

    # Side outline lines
    draw.line([(x1, y1 + ry), (x1, y2 - ry)], fill=outline_color, width=stroke_w)
    draw.line([(x2, y1 + ry), (x2, y2 - ry)], fill=outline_color, width=stroke_w)
    
    # Bottom curved outline (arc only, no chord)
    draw.arc([x1, y2 - 2 * ry, x2, y2], start=0, end=180, fill=outline_color, width=stroke_w)
    
    # Top full ellipse
    draw.ellipse([x1, y1, x2, y1 + 2 * ry], fill=fill_color, outline=outline_color, width=stroke_w)

def draw_actor(draw, x, y, label="Người dùng", font=None, stroke_w=3):
    """Draw UML actor stick figure"""
    r = 24  # Head radius
    # Head
    draw.ellipse([x - r, y - r, x + r, y + r], outline='#222222', fill='#FFFFFF', width=stroke_w)
    # Torso
    draw.line([(x, y + r), (x, y + 80)], fill='#222222', width=stroke_w)
    # Arms
    draw.line([(x - 42, y + 36), (x + 42, y + 36)], fill='#222222', width=stroke_w)
    # Left leg
    draw.line([(x, y + 80), (x - 32, y + 130)], fill='#222222', width=stroke_w)
    # Right leg
    draw.line([(x, y + 80), (x + 32, y + 130)], fill='#222222', width=stroke_w)
    # Text label
    if font:
        draw.text((x, y + 160), label, fill='#000000', font=font, anchor='mm')

def draw_arrow(draw, p1, p2, color='#222222', width=3, arrow_size=15):
    """Draw straight line with sharp solid arrowhead"""
    x1, y1 = p1
    x2, y2 = p2
    draw.line([p1, p2], fill=color, width=width)
    
    # Calculate arrowhead triangle
    angle = math.atan2(y2 - y1, x2 - x1)
    angle_offset = math.pi / 7.5  # ~24 degrees
    
    xa = x2 - arrow_size * math.cos(angle - angle_offset)
    ya = y2 - arrow_size * math.sin(angle - angle_offset)
    xb = x2 - arrow_size * math.cos(angle + angle_offset)
    yb = y2 - arrow_size * math.sin(angle + angle_offset)
    
    draw.polygon([(x2, y2), (xa, ya), (xb, yb)], fill=color)

def draw_curved_arrow(draw, p_start, p_control, p_end, color='#222222', width=3, arrow_size=15):
    """Draw quadratic bezier curve with arrowhead"""
    num_pts = 40
    pts = []
    for i in range(num_pts + 1):
        t = i / float(num_pts)
        bx = (1 - t)**2 * p_start[0] + 2 * (1 - t) * t * p_control[0] + t**2 * p_end[0]
        by = (1 - t)**2 * p_start[1] + 2 * (1 - t) * t * p_control[1] + t**2 * p_end[1]
        pts.append((bx, by))
    
    # Draw polyline segments
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=color, width=width)
        
    # Draw arrow at end point based on last segment vector
    p_last = pts[-2]
    p_final = pts[-1]
    angle = math.atan2(p_final[1] - p_last[1], p_final[0] - p_last[0])
    angle_offset = math.pi / 7.5
    
    xa = p_final[0] - arrow_size * math.cos(angle - angle_offset)
    ya = p_final[1] - arrow_size * math.sin(angle - angle_offset)
    xb = p_final[0] - arrow_size * math.cos(angle + angle_offset)
    yb = p_final[1] - arrow_size * math.sin(angle + angle_offset)
    
    draw.polygon([p_final, (xa, ya), (xb, yb)], fill=color)

def generate_uml_diagram(output_path):
    # Ultra-high definition canvas: 2400 x 2050 for razor-sharp printing and viewing
    width = 2400
    height = 2050
    img = Image.new('RGB', (width, height), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    # Load high-quality true-type fonts
    font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_path_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_path_serif_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

    font_title = ImageFont.truetype(font_path_bold, 44)
    font_box_header = ImageFont.truetype(font_path_bold, 34)
    font_comp_title = ImageFont.truetype(font_path_bold, 30)
    font_comp_sub = ImageFont.truetype(font_path_reg, 26)
    font_actor = ImageFont.truetype(font_path_reg, 32)
    font_label = ImageFont.truetype(font_path_reg, 28)
    font_caption = ImageFont.truetype(font_path_serif_bold, 34)

    # 1. Main Title (Top Header)
    draw.text((width // 2, 75), "Sơ đồ kiến trúc hệ thống Website Tuyển dụng (Job Board DevOps)", fill='#000000', font=font_title, anchor='mm')

    # 2. Actor: Người dùng (Top Right)
    actor_x = 1750
    actor_y = 175
    draw_actor(draw, actor_x, actor_y, "Người dùng", font=font_actor, stroke_w=3)

    # 3. Outer Deployment Node: Docker Compose (máy chủ Ubuntu)
    outer_x1 = 120
    outer_y1 = 530
    outer_x2 = 2280
    outer_y2 = 1860
    draw.rounded_rectangle([outer_x1, outer_y1, outer_x2, outer_y2], radius=10, fill='#FFFFFF', outline='#222222', width=3)
    # Centered Header
    draw.text((width // 2, outer_y1 + 35), "Docker Compose (máy chủ Ubuntu)", fill='#000000', font=font_box_header, anchor='mm')

    # 4. Left Node: Giám sát và log tập trung
    # Clean spacing: 180 to 1260 (gap to 1420 is 160px for proxy arrow)
    left_x1 = 180
    left_y1 = 620
    left_x2 = 1260
    left_y2 = 1800
    draw.rounded_rectangle([left_x1, left_y1, left_x2, left_y2], radius=8, fill='#FFFFFF', outline='#333333', width=3)
    draw.text(((left_x1 + left_x2) // 2, left_y1 + 40), "Giám sát và log tập trung", fill='#000000', font=font_box_header, anchor='mm')

    # Components inside Left Node (Faithful to layout of reference diagram):
    # 4.1. Grafana (Top Right inside Left Node)
    g_x1 = 900; g_y1 = 730; g_x2 = 1170; g_y2 = 860
    draw.rectangle([g_x1, g_y1, g_x2, g_y2], fill='#FAFAFA', outline='#333333', width=3)
    draw_component_icon(draw, g_x2 - 44, g_y1 + 10)
    draw.text(((g_x1 + g_x2) // 2, (g_y1 + g_y2) // 2 + 2), "Grafana", fill='#000000', font=font_comp_title, anchor='mm')

    # 4.2. Loki (Middle Left inside Left Node - directly above Promtail)
    lk_x1 = 440; lk_y1 = 1120; lk_x2 = 680; lk_y2 = 1240
    draw.rectangle([lk_x1, lk_y1, lk_x2, lk_y2], fill='#FAFAFA', outline='#333333', width=3)
    draw_component_icon(draw, lk_x2 - 44, lk_y1 + 10)
    draw.text(((lk_x1 + lk_x2) // 2, (lk_y1 + lk_y2) // 2 + 2), "Loki", fill='#000000', font=font_comp_title, anchor='mm')

    # 4.3. Prometheus (Middle Right inside Left Node - directly below Grafana)
    pr_x1 = 860; pr_y1 = 1120; pr_x2 = 1200; pr_y2 = 1240
    draw.rectangle([pr_x1, pr_y1, pr_x2, pr_y2], fill='#FAFAFA', outline='#333333', width=3)
    draw_component_icon(draw, pr_x2 - 44, pr_y1 + 10)
    draw.text(((pr_x1 + pr_x2) // 2, (pr_y1 + pr_y2) // 2 + 2), "Prometheus", fill='#000000', font=font_comp_title, anchor='mm')

    # 4.4. Promtail (Bottom Left inside Left Node)
    pt_x1 = 220; pt_y1 = 1520; pt_x2 = 650; pt_y2 = 1680
    draw.rectangle([pt_x1, pt_y1, pt_x2, pt_y2], fill='#FAFAFA', outline='#333333', width=3)
    draw_component_icon(draw, pt_x2 - 44, pt_y1 + 10)
    draw.text((pt_x1 + 30, pt_y1 + 42), "Promtail", fill='#000000', font=font_comp_title)
    draw.text((pt_x1 + 30, pt_y1 + 92), "(đọc log container)", fill='#333333', font=font_comp_sub)

    # 4.5. Exporters (Bottom Right inside Left Node)
    ex_x1 = 800; ex_y1 = 1520; ex_x2 = 1240; ex_y2 = 1680
    draw.rectangle([ex_x1, ex_y1, ex_x2, ex_y2], fill='#FAFAFA', outline='#333333', width=3)
    draw_component_icon(draw, ex_x2 - 44, ex_y1 + 10)
    draw.text((ex_x1 + 30, pt_y1 + 42), "Exporters", fill='#000000', font=font_comp_title)
    draw.text((ex_x1 + 30, pt_y1 + 92), "(container, web, DB)", fill='#333333', font=font_comp_sub)

    # 5. Right Top 3D Node: Reverse Proxy
    rp_x1 = 1420; rp_y1 = 660; rp_x2 = 2120; rp_y2 = 960
    draw_3d_box(draw, rp_x1, rp_y1, rp_x2, rp_y2, depth_x=22, depth_y=22, stroke_w=3)
    draw.text(((rp_x1 + rp_x2) // 2, rp_y1 + 34), "Reverse Proxy", fill='#000000', font=font_box_header, anchor='mm')

    # Inside Reverse Proxy: Nginx Component
    nx_x1 = 1460; nx_y1 = 740; nx_x2 = 2080; nx_y2 = 910
    draw.rectangle([nx_x1, nx_y1, nx_x2, nx_y2], fill='#FFFFFF', outline='#333333', width=3)
    draw_component_icon(draw, nx_x2 - 44, nx_y1 + 10)
    draw.text((nx_x1 + 30, nx_y1 + 34), "Nginx", fill='#000000', font=font_comp_title)
    draw.text((nx_x1 + 30, nx_y1 + 86), "HTTPS + security headers", fill='#333333', font=font_comp_sub)

    # 6. Right Middle 3D Node: Ứng dụng
    app_x1 = 1420; app_y1 = 1080; app_x2 = 2220; app_y2 = 1360
    draw_3d_box(draw, app_x1, app_y1, app_x2, app_y2, depth_x=22, depth_y=22, stroke_w=3)
    draw.text(((app_x1 + app_x2) // 2, app_y1 + 34), "Ứng dụng", fill='#000000', font=font_box_header, anchor='mm')

    # Components inside Ứng dụng:
    # 6.1. Web Node.js
    web_x1 = 1460; web_y1 = 1160; web_x2 = 1760; web_y2 = 1290
    draw.rectangle([web_x1, web_y1, web_x2, web_y2], fill='#FFFFFF', outline='#333333', width=3)
    draw_component_icon(draw, web_x2 - 44, web_y1 + 10)
    draw.text(((web_x1 + web_x2) // 2, (web_y1 + web_y2) // 2 + 2), "Web Node.js", fill='#000000', font=font_comp_title, anchor='mm')

    # 6.2. phpMyAdmin
    pma_x1 = 1870; pma_y1 = 1160; pma_x2 = 2170; pma_y2 = 1290
    draw.rectangle([pma_x1, pma_y1, pma_x2, pma_y2], fill='#FFFFFF', outline='#333333', width=3)
    draw_component_icon(draw, pma_x2 - 44, pma_y1 + 10)
    draw.text(((pma_x1 + pma_x2) // 2, (pma_y1 + pma_y2) // 2 + 2), "phpMyAdmin", fill='#000000', font=font_comp_title, anchor='mm')

    # 7. Database Cylinder: MySQL
    db_x1 = 1650; db_y1 = 1520; db_x2 = 1880; db_y2 = 1680
    draw_cylinder(draw, db_x1, db_y1, db_x2, db_y2, fill_color='#FAFAFA', stroke_w=3)
    draw.text(((db_x1 + db_x2) // 2, (db_y1 + db_y2) // 2 + 8), "MySQL", fill='#000000', font=font_comp_title, anchor='mm')

    # =========================================================================
    # ARROWS & LABELS (PERFECTLY MATCHING REFERENCE IMAGE, NO OVERLAPS)
    # =========================================================================

    # 1. Người dùng -> Nginx (HTTPS)
    draw_arrow(draw, (actor_x, actor_y + 185), (actor_x, rp_y1 - 22), color='#222222', width=3, arrow_size=16)
    draw.text((actor_x + 18, 420), "HTTPS", fill='#000000', font=font_label)

    # 2. Nginx -> Grafana (proxy)
    # Clear horizontal arrow crossing between rp_x1 (1420) and left_x2 (1260) into Grafana g_x2 (1170)
    draw_arrow(draw, (nx_x1, 795), (g_x2, 795), color='#222222', width=3, arrow_size=16)
    # Label placed neatly in the middle gap above the arrow with white backing so it never collides
    label_px = "proxy"
    draw.rectangle([(1280, 750), (1360, 785)], fill='#FFFFFF')
    draw.text((1320, 768), label_px, fill='#000000', font=font_label, anchor='mm')

    # 3. Nginx -> Web Node.js (proxy)
    draw_arrow(draw, (1660, nx_y2), (1610, web_y1), color='#222222', width=3, arrow_size=16)
    draw.text((1550, 1025), "proxy", fill='#000000', font=font_label)

    # 4. Nginx -> phpMyAdmin (proxy)
    draw_arrow(draw, (1880, nx_y2), (1980, pma_y1), color='#222222', width=3, arrow_size=16)
    draw.text((1965, 1025), "proxy", fill='#000000', font=font_label)

    # 5. Web Node.js -> MySQL (SQL)
    draw_arrow(draw, (1610, web_y2), (1700, db_y1 + 10), color='#222222', width=3, arrow_size=16)
    draw.text((1595, 1420), "SQL", fill='#000000', font=font_label)

    # 6. phpMyAdmin -> MySQL (SQL)
    draw_arrow(draw, (2020, pma_y2), (1840, db_y1 + 10), color='#222222', width=3, arrow_size=16)
    draw.text((1965, 1420), "SQL", fill='#000000', font=font_label)

    # 7. Grafana -> Loki (log)
    draw_arrow(draw, (900, 840), (630, lk_y1), color='#222222', width=3, arrow_size=16)
    draw.text((720, 960), "log", fill='#000000', font=font_label)

    # 8. Grafana -> Prometheus (metrics)
    draw_arrow(draw, (1030, g_y2), (1030, pr_y1), color='#222222', width=3, arrow_size=16)
    draw.text((1045, 980), "metrics", fill='#000000', font=font_label)

    # 9. Promtail -> Loki (đẩy log)
    draw_arrow(draw, (490, pt_y1), (540, lk_y2), color='#222222', width=3, arrow_size=16)
    draw.text((550, 1370), "đẩy log", fill='#000000', font=font_label)

    # 10. Exporters -> Prometheus (thu metrics)
    p_ex_start = (940, ex_y1)
    p_control = (870, 1370)
    p_pr_end = (960, pr_y2)
    draw_curved_arrow(draw, p_ex_start, p_control, p_pr_end, color='#222222', width=3, arrow_size=16)
    draw.text((860, 1375), "thu metrics", fill='#000000', font=font_label, anchor='ra')

    # 11. Bottom Figure Caption
    draw.text((width // 2, 1960), "Hình 1.1: Sơ đồ kiến trúc tổng thể hệ thống", fill='#000000', font=font_caption, anchor='mm')

    # Save ultra-high resolution image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG', dpi=(300, 300), optimize=True)
    print(f"[SUCCESS] High-res PNG diagram created successfully at: {output_path}")

def generate_svg_diagram(svg_path):
    """Generate pure SVG vector diagram for infinite scalability"""
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1025" width="100%" height="100%" style="background-color: #ffffff; font-family: 'DejaVu Sans', Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#222222"/>
    </marker>
  </defs>

  <!-- Title -->
  <text x="600" y="38" text-anchor="middle" font-size="21" font-weight="bold" fill="#000000">Sơ đồ kiến trúc hệ thống Website Tuyển dụng (Job Board DevOps)</text>

  <!-- Actor: Người dùng -->
  <g transform="translate(875, 50)">
    <circle cx="0" cy="30" r="12" fill="#ffffff" stroke="#222222" stroke-width="1.8"/>
    <line x1="0" y1="42" x2="0" y2="82" stroke="#222222" stroke-width="1.8"/>
    <line x1="-21" y1="60" x2="21" y2="60" stroke="#222222" stroke-width="1.8"/>
    <line x1="0" y1="82" x2="-16" y2="108" stroke="#222222" stroke-width="1.8"/>
    <line x1="0" y1="82" x2="16" y2="108" stroke="#222222" stroke-width="1.8"/>
    <text x="0" y="124" text-anchor="middle" font-size="15" fill="#000000">Người dùng</text>
  </g>

  <!-- Arrow HTTPS -->
  <line x1="875" y1="180" x2="875" y2="318" stroke="#222222" stroke-width="1.8" marker-end="url(#arrow)"/>
  <text x="886" y="225" font-size="14" fill="#000000">HTTPS</text>

  <!-- Outer Box: Docker Compose -->
  <rect x="60" y="265" width="1080" height="665" rx="6" fill="#ffffff" stroke="#222222" stroke-width="1.8"/>
  <text x="600" y="284" text-anchor="middle" font-size="17" font-weight="bold" fill="#000000">Docker Compose (máy chủ Ubuntu)</text>

  <!-- Left Container: Giám sát và log tập trung -->
  <rect x="90" y="310" width="540" height="590" rx="4" fill="#ffffff" stroke="#333333" stroke-width="1.8"/>
  <text x="360" y="332" text-anchor="middle" font-size="17" font-weight="bold" fill="#000000">Giám sát và log tập trung</text>

  <!-- Grafana -->
  <g id="comp-grafana">
    <rect x="450" y="365" width="135" height="65" fill="#fafafa" stroke="#333333" stroke-width="1.6"/>
    <rect x="563" y="371" width="16" height="10" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="561" y="373" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="561" y="377" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <text x="517" y="405" text-anchor="middle" font-size="15" font-weight="bold" fill="#000000">Grafana</text>
  </g>

  <!-- Loki -->
  <g id="comp-loki">
    <rect x="220" y="560" width="120" height="60" fill="#fafafa" stroke="#333333" stroke-width="1.6"/>
    <rect x="323" y="566" width="16" height="10" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="321" y="568" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="321" y="572" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <text x="280" y="597" text-anchor="middle" font-size="15" font-weight="bold" fill="#000000">Loki</text>
  </g>

  <!-- Prometheus -->
  <g id="comp-prometheus">
    <rect x="430" y="560" width="170" height="60" fill="#fafafa" stroke="#333333" stroke-width="1.6"/>
    <rect x="583" y="566" width="16" height="10" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="581" y="568" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="581" y="572" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <text x="515" y="597" text-anchor="middle" font-size="15" font-weight="bold" fill="#000000">Prometheus</text>
  </g>

  <!-- Promtail -->
  <g id="comp-promtail">
    <rect x="110" y="760" width="215" height="80" fill="#fafafa" stroke="#333333" stroke-width="1.6"/>
    <rect x="308" y="766" width="16" height="10" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="306" y="768" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="306" y="772" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <text x="125" y="792" font-size="15" font-weight="bold" fill="#000000">Promtail</text>
    <text x="125" y="818" font-size="13" fill="#333333">(đọc log container)</text>
  </g>

  <!-- Exporters -->
  <g id="comp-exporters">
    <rect x="400" y="760" width="220" height="80" fill="#fafafa" stroke="#333333" stroke-width="1.6"/>
    <rect x="603" y="766" width="16" height="10" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="601" y="768" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="601" y="772" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <text x="415" y="792" font-size="15" font-weight="bold" fill="#000000">Exporters</text>
    <text x="415" y="818" font-size="13" fill="#333333">(container, web, DB)</text>
  </g>

  <!-- Arrows in Monitoring Container -->
  <!-- Grafana -> Loki (log) -->
  <line x1="450" y1="420" x2="315" y2="560" stroke="#222222" stroke-width="1.6" marker-end="url(#arrow)"/>
  <text x="360" y="480" font-size="14" fill="#000000">log</text>

  <!-- Grafana -> Prometheus (metrics) -->
  <line x1="515" y1="430" x2="515" y2="560" stroke="#222222" stroke-width="1.6" marker-end="url(#arrow)"/>
  <text x="523" y="490" font-size="14" fill="#000000">metrics</text>

  <!-- Promtail -> Loki (đẩy log) -->
  <line x1="245" y1="760" x2="270" y2="620" stroke="#222222" stroke-width="1.6" marker-end="url(#arrow)"/>
  <text x="275" y="685" font-size="14" fill="#000000">đẩy log</text>

  <!-- Exporters -> Prometheus (thu metrics) -->
  <path d="M 470 760 Q 435 685 480 620" fill="none" stroke="#222222" stroke-width="1.6" marker-end="url(#arrow)"/>
  <text x="430" y="688" text-anchor="end" font-size="14" fill="#000000">thu metrics</text>

  <!-- Right Section: Reverse Proxy 3D Node -->
  <g id="node-reverse-proxy">
    <polygon points="710,330 721,319 1071,319 1060,330" fill="#fafafa" stroke="#222222" stroke-width="1.6"/>
    <polygon points="1060,330 1071,319 1071,469 1060,480" fill="#f0f2f5" stroke="#222222" stroke-width="1.6"/>
    <rect x="710" y="330" width="350" height="150" fill="#ffffff" stroke="#222222" stroke-width="1.6"/>
    <text x="885" y="348" text-anchor="middle" font-size="17" font-weight="bold" fill="#000000">Reverse Proxy</text>

    <!-- Nginx component -->
    <rect x="730" y="370" width="310" height="85" fill="#ffffff" stroke="#333333" stroke-width="1.6"/>
    <rect x="1021" y="376" width="16" height="10" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="1019" y="378" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="1019" y="382" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <text x="745" y="398" font-size="15" font-weight="bold" fill="#000000">Nginx</text>
    <text x="745" y="424" font-size="13" fill="#333333">HTTPS + security headers</text>
  </g>

  <!-- Horizontal Arrow: Nginx -> Grafana (proxy) -->
  <line x1="730" y1="398" x2="585" y2="398" stroke="#222222" stroke-width="1.6" marker-end="url(#arrow)"/>
  <rect x="635" y="383" width="50" height="18" fill="#ffffff"/>
  <text x="660" y="396" text-anchor="middle" font-size="14" fill="#000000">proxy</text>

  <!-- Right Section: Ứng dụng 3D Node -->
  <g id="node-ung-dung">
    <polygon points="710,540 721,529 1121,529 1110,540" fill="#fafafa" stroke="#222222" stroke-width="1.6"/>
    <polygon points="1110,540 1121,529 1121,669 1110,680" fill="#f0f2f5" stroke="#222222" stroke-width="1.6"/>
    <rect x="710" y="540" width="400" height="140" fill="#ffffff" stroke="#222222" stroke-width="1.6"/>
    <text x="910" y="558" text-anchor="middle" font-size="17" font-weight="bold" fill="#000000">Ứng dụng</text>

    <!-- Web Node.js -->
    <rect x="730" y="580" width="150" height="65" fill="#ffffff" stroke="#333333" stroke-width="1.6"/>
    <rect x="861" y="586" width="16" height="10" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="859" y="588" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="859" y="592" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <text x="805" y="618" text-anchor="middle" font-size="15" font-weight="bold" fill="#000000">Web Node.js</text>

    <!-- phpMyAdmin -->
    <rect x="935" y="580" width="150" height="65" fill="#ffffff" stroke="#333333" stroke-width="1.6"/>
    <rect x="1066" y="586" width="16" height="10" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="1064" y="588" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <rect x="1064" y="592" width="4" height="2" fill="#ffffff" stroke="#333333" stroke-width="1"/>
    <text x="1010" y="618" text-anchor="middle" font-size="15" font-weight="bold" fill="#000000">phpMyAdmin</text>
  </g>

  <!-- Arrows from Nginx to Ứng dụng -->
  <!-- Nginx -> Web Node.js (proxy) -->
  <line x1="830" y1="455" x2="805" y2="580" stroke="#222222" stroke-width="1.6" marker-end="url(#arrow)"/>
  <text x="780" y="513" font-size="14" fill="#000000">proxy</text>

  <!-- Nginx -> phpMyAdmin (proxy) -->
  <line x1="940" y1="455" x2="990" y2="580" stroke="#222222" stroke-width="1.6" marker-end="url(#arrow)"/>
  <text x="982" y="513" font-size="14" fill="#000000">proxy</text>

  <!-- Bottom Node: MySQL 3D Cylinder -->
  <g id="node-mysql">
    <path d="M 825,771 L 825,829 A 57.5,11 0 0,0 940,829 L 940,771 Z" fill="#fafafa"/>
    <path d="M 825,829 A 57.5,11 0 0,0 940,829" fill="none" stroke="#222222" stroke-width="1.6"/>
    <line x1="825" y1="771" x2="825" y2="829" stroke="#222222" stroke-width="1.6"/>
    <line x1="940" y1="771" x2="940" y2="829" stroke="#222222" stroke-width="1.6"/>
    <ellipse cx="882.5" cy="771" rx="57.5" ry="11" fill="#fafafa" stroke="#222222" stroke-width="1.6"/>
    <text x="882.5" y="808" text-anchor="middle" font-size="15" font-weight="bold" fill="#000000">MySQL</text>
  </g>

  <!-- Arrows from Ứng dụng to MySQL -->
  <!-- Web Node.js -> MySQL (SQL) -->
  <line x1="805" y1="645" x2="850" y2="765" stroke="#222222" stroke-width="1.6" marker-end="url(#arrow)"/>
  <text x="798" y="710" font-size="14" fill="#000000">SQL</text>

  <!-- phpMyAdmin -> MySQL (SQL) -->
  <line x1="1010" y1="645" x2="920" y2="765" stroke="#222222" stroke-width="1.6" marker-end="url(#arrow)"/>
  <text x="982" y="710" font-size="14" fill="#000000">SQL</text>

  <!-- Bottom Caption -->
  <text x="600" y="980" text-anchor="middle" font-size="17" font-weight="bold" font-family="'Times New Roman', serif" fill="#000000">Hình 1.1: Sơ đồ kiến trúc tổng thể hệ thống</text>
</svg>
'''
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg.strip())
    print(f"[SUCCESS] Scalable SVG diagram created successfully at: {svg_path}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_png = os.path.join(script_dir, "screenshots", "system_architecture.png")
    target_svg = os.path.join(script_dir, "screenshots", "system_architecture.svg")
    generate_uml_diagram(target_png)
    generate_svg_diagram(target_svg)

