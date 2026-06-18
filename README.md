Markdown
# 🛡️ Hệ thống Giám sát & Chống thất thoát dữ liệu thời gian thực (DLP Dashboard)

Dự án nghiên cứu xây dựng giải pháp DLP tích hợp cổng xác thực phân tầng 2FA qua ứng dụng di động phục vụ đồ án môn học.

##  Hướng dẫn cài đặt và Khởi chạy

### 1. Chuẩn bị môi trường
```bash
# Khởi tạo môi trường ảo Python
python -m venv .venv

# Kích hoạt môi trường ảo (Windows)
.venv\Scripts\activate

2. Cài đặt các thư viện lõi

pip install streamlit watchdog pyotp qrcode pillow requests

3. Khấu hình hệ thống
Mở file app.py và điền đường link Discord Webhook của bạn vào biến DISCORD_WEBHOOK_URL.

4. Khởi chạy ứng dụng Web Dashboard

streamlit run app.py