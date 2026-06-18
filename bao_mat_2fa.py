import os
import random
import time
import qrcode
import string
import json

# Tên file lưu cache mã OTP tạm thời
FILE_OTP_CACHE = "zalo_otp_cache.json"

def sinh_ma_otp_ngau_nhien(do_dai=6):
    """Sinh chuỗi 6 số ngẫu nhiên phục vụ gửi qua Zalo/Discord Gateway"""
    ky_tu = string.digits
    return ''.join(random.choice(ky_tu) for _ in range(do_dai))

def khoi_tao_he_thong_zalo_2fa():
    """
    Tạo mã OTP mới, cấu hình đường link Deep Link Zalo và xuất ảnh QR Code.
    """
    # 1. Sinh mã OTP mới và thiết lập thời gian hết hạn là 2 phút (120 giây)
    ma_otp = sinh_ma_otp_ngau_nhien()
    thoi_gian_tao = time.time()
    
    du_lieu_cache = {
        "otp": ma_otp,
        "expires_at": thoi_gian_tao + 120  # Hết hạn sau 120 giây
    }
    
    # Ghi mã OTP tạm thời vào file json để đối chiếu lúc bấm xác minh trên Web
    with open(FILE_OTP_CACHE, "w", encoding="utf-8") as f:
        json.dump(du_lieu_cache, f, ensure_ascii=False, indent=4)

    # 2. Tạo đường link Deep Link của Zalo để khi quét bằng Zalo App sẽ hiểu được
    link_zalo_gateway = f"https://zalo.me/g/bmudht_dlp_otp?code={ma_otp}"

    # 3. Xuất file ảnh QR để hiển thị lên giao diện Web Streamlit
    file_anh_qr = "qrcode_2fa.png"
    if os.path.exists(file_anh_qr):
        try: os.remove(file_anh_qr)
        except Exception: pass
        
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(link_zalo_gateway)
    qr.make(fit=True)
    
    anh_qr = qr.make_image(fill_color="black", back_color="white")
    anh_qr.save(file_anh_qr)
    
    return ma_otp

def xac_thuc_ma_zalo_otp(ma_nhap_vao):
    """Kiểm tra mã OTP nhập từ giao diện Web đối chiếu với mã hệ thống đã sinh ra"""
    if not os.path.exists(FILE_OTP_CACHE):
        return False
        
    try:
        with open(FILE_OTP_CACHE, "r", encoding="utf-8") as f:
            du_lieu = json.load(f)
            
        # Kiểm tra nếu thời gian hiện tại vượt quá thời gian hết hạn
        if time.time() > du_lieu.get("expires_at", 0):
            return False
            
        # So sánh mã người dùng nhập vào với mã lưu trong cache
        return str(du_lieu.get("otp")) == str(ma_nhap_vao).strip()
    except Exception:
        return False