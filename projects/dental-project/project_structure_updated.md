# Cấu trúc Dự Án (Nha Khoa Minh Sinh) - Tinh Gọn 2 Cổng (WordPress + Django)

Tài liệu này lưu trữ tại `D:\Thành\Agent\projects\dental-project\project_structure_updated.md`.

## 1. Kiến trúc Tinh gọn 2 Dịch vụ (Đã loại bỏ hoàn toàn Next.js cổng 3000)

| Dịch vụ | Cổng (Port) | Công nghệ | Nhiệm vụ chính |
| :--- | :--- | :--- | :--- |
| **WordPress** | **Cổng 80** (`http://localhost`) | PHP 8.2 + Apache + MariaDB | Trang chủ Landing Page, Giới thiệu phòng khám, Chuyên mục dịch vụ, Toàn bộ Blog tin tức SEO (Rank Math, Elementor/Gutenberg). Nút CTA chuyển thẳng sang Django. |
| **Django Backend** | **Cổng 8000** (`http://localhost:8000`) | Python 3.12 + Django 6.1 | Quản trị phòng khám Unfold Admin, POS thu ngân, Quản lý khách hàng, REST API.<br>• **Đã tích hợp Form Đặt lịch (`/booking/`):** React Standalone Bundle.<br>• **Đã tích hợp Sơ đồ răng (`/dental-chart/`):** React SVG Standalone Bundle. |

## 2. Cấu trúc Thư mục

```text
dental_project/
├── docker-compose.yml              # Chỉ còn 3 containers: dental_backend (8000), dental_wordpress (80), dental_wp_db (3306)
├── backend/                        # Django Backend (Cổng 8000)
│   ├── templates/
│   │   ├── booking_standalone.html # Template phục vụ Form Đặt lịch trực tiếp
│   │   ├── dental_chart_standalone.html # Template phục vụ Sơ đồ răng trực tiếp
│   │   └── admin/
│   │       ├── customer_360.html   # Bệnh án 360 (Iframe sơ đồ răng trỏ nội bộ /dental-chart/)
│   │       └── pos_system.html
│   ├── static/js/
│   │   ├── booking_app.bundle.js   # Bundle React ma trận ghế khám (259 KB)
│   │   └── dental_chart_app.bundle.js # Bundle React sơ đồ răng SVG (223 KB)
│   └── core/urls.py                # Định tuyến /booking/ và /dental-chart/
├── wordpress/                      # WordPress Content (Cổng 80)
│   └── wp-content/themes/minhsinh-dental/ # Custom Theme Minh Sinh Dental
└── frontend/                       # Thư mục mã nguồn React gốc (Dùng khi cần compile lại bundle qua build_bundles.js)
```
