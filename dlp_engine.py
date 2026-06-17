import re
import json # Thư viện để bóc tách cấu trúc file JSON

# ========================================================
# HÀM KIỂM TRA THUẬT TOÁN LUHN (Xác thực thẻ tín dụng thật)
# ========================================================
def kiem_tra_thuan_toan_luhn(chuoi_so):
    try:
        cac_chu_so = [int(x) for x in chuoi_so]
        for i in range(len(cac_chu_so) - 2, -1, -2):
            cac_chu_so[i] *= 2
            if cac_chu_so[i] > 9:
                cac_chu_so[i] -= 9
        return sum(cac_chu_so) % 10 == 0
    except Exception:
        return False

# ========================================================
# 1. CÁC HÀM QUÉT TÌM (BỘ LỌC THÔNG MINH TOÀN CẦU)
# ========================================================
def quat_tim_email(van_ban):
    khuon_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(khuon_email, van_ban)

def quat_tim_sdt(van_ban):
    khuon_sdt_quoc_te = r'\+(?:[0-9]\s*?){7,15}\b'
    khuon_sdt_viet_nam = r'\b0[3|5|7|8|9][0-9]\s*?[0-9]{3}\s*?[0-9]{4}\b'
    sdt_quoc_te = re.findall(khuon_sdt_quoc_te, van_ban)
    sdt_viet_nam = re.findall(khuon_sdt_viet_nam, van_ban)
    danh_sach_tong = sdt_quoc_te + sdt_viet_nam
    return [re.sub(r'[\s-]', '', sdt) for sdt in danh_sach_tong]

def quat_tim_the_tin_dung(van_ban):
    khuon_the = r'\b[0-9]{16}\b'
    danh_sach_tho = re.findall(khuon_the, van_ban)
    return [the for the in danh_sach_tho if kiem_tra_thuan_toan_luhn(the)]

def quat_tim_openai_key(van_ban):
    khuon_openai = r'\bsk-[a-zA-Z0-9]{48}\b'
    return re.findall(khuon_openai, van_ban)

# --- TÍNH NĂNG MỚI: QUÉT ĐỆ QUY CẤU TRÚC JSON ---
def quat_cau_truc_json(du_lieu_json, cac_loi_phat_hien):
    """Hàm đệ quy đi sâu vào từng ngóc ngách của file JSON để tìm các Key nhạy cảm"""
    # Các từ khóa thường được dùng để đặt tên cho mật khẩu hoặc token
    tu_khoa_nguy_hiem = ["password", "passwd", "secret", "token", "api_key", "private_key", "db_pass"]
    
    if isinstance(du_lieu_json, dict):
        for key, value in du_lieu_json.items():
            # Nếu phát hiện Tên Key nằm trong danh sách nguy hiểm và Giá trị của nó là chuỗi chữ rõ (Plaintext)
            if any(tk in key.lower() for tk in tu_khoa_nguy_hiem) and isinstance(value, str) and value:
                # Loại trừ trường hợp chuỗi đã bị che mờ từ trước
                if "*" not in value:
                    cac_loi_phat_hien.append(f"Cấu trúc Key nhạy cảm: '{key}'")
            # Đệ quy đi sâu tiếp nếu Value là một Object lồng nhau
            quat_cau_truc_json(value, cac_loi_phat_hien)
            
    elif isinstance(du_lieu_json, list):
        for item in du_lieu_json:
            quat_cau_truc_json(item, cac_loi_phat_hien)

# ========================================================
# 2. CÁC HÀM CHE MỜ (MASKING)
# ========================================================
def che_mo_email(van_ban):
    khuon_email_chi_tiet = r'(\w)(\w+)(\w@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    return re.sub(khuon_email_chi_tiet, r'\1*****\3', van_ban)

def che_mo_sdt(van_ban):
    khuon_quoc_te = r'(\+[0-9]{1,3}[\s-]*[0-9])([\s0-9-]+)([0-9][\s-]*[0-9][\s-]*[0-9]\b)'
    def thay_the_quoc_te(match):
        cum_dau, cum_giua, cum_cuoi = match.group(1), match.group(2), match.group(3)
        cum_giua_che = re.sub(r'[0-9]', '*', cum_giua)
        return cum_dau + cum_giua_che + cum_cuoi
    van_ban = re.sub(khuon_quoc_te, thay_the_quoc_te, van_ban)

    khuon_viet_nam = r'\b(0[3|5|7|8|9][0-9])([\s0-9-]+)([0-9]{3}\b)'
    def thay_the_viet_nam(match):
        cum_dau, cum_giua, cum_cuoi = match.group(1), match.group(2), match.group(3)
        cum_giua_che = re.sub(r'[0-9]', '*', cum_giua)
        return cum_dau + cum_giua_che + cum_cuoi
    van_ban = re.sub(khuon_viet_nam, thay_the_viet_nam, van_ban)
    return van_ban

def che_mo_the_tin_dung(van_ban):
    danh_sach_the = quat_tim_the_tin_dung(van_ban)
    for the in danh_sach_the:
        the_che = the[:4] + "************"
        van_ban = van_ban.replace(the, the_che)
    return van_ban

def che_mo_openai_key(van_ban):
    khuon_openai_chi_tiet = r'\b(sk-[a-zA-Z0-9]{3})([a-zA-Z0-9]{45})\b'
    return re.sub(khuon_openai_chi_tiet, r'\1************', van_ban)

# --- TÍNH NĂNG MỚI: CHE MỜ ĐỆ QUY CHO FILE JSON ---
def che_mo_cau_truc_json(du_lieu_json):
    """Hàm tự động băm giá trị của các Key nhạy cảm trong Object JSON thành dấu *"""
    tu_khoa_nguy_hiem = ["password", "passwd", "secret", "token", "api_key", "private_key", "db_pass"]
    
    if isinstance(du_lieu_json, dict):
        for key, value in du_lieu_json.items():
            if any(tk in key.lower() for tk in tu_khoa_nguy_hiem) and isinstance(value, str) and value:
                if "*" not in value:
                    du_lieu_json[key] = "********"
            else:
                che_mo_cau_truc_json(value)
    elif isinstance(du_lieu_json, list):
        for item in du_lieu_json:
            che_mo_cau_truc_json(item)