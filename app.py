import streamlit as st
import bao_mat_2fa
import dlp_engine
import os
import json
import time
import requests
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ========================================================
# 1. CẤU HÌNH HỆ THỐNG VÀ THÔNG TIN ĐƯỜNG MẠNG
# ========================================================
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"

PHIEN_BAN_HE_THONG = "DLP Monitor v3.0 Pro"

st.set_page_config(
    page_title="BMUDHT - Hệ thống Trung tâm DLP Web Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Khởi tạo các trạng thái lưu trữ phiên làm việc của Streamlit
if 'lop_1_thanh_cong' not in st.session_state:
    st.session_state.lop_1_thanh_cong = False
if 'lop_2_thanh_cong' not in st.session_state:
    st.session_state.lop_2_thanh_cong = False
if 'observer_instance' not in st.session_state:
    st.session_state.observer_instance = None
if 'ma_otp_zalo' not in st.session_state:
    st.session_state.ma_otp_zalo = None

# ========================================================
# 2. GIAO DIỆN TÙY CHỈNH (THEME "TRUNG TÂM ĐIỀU HÀNH AN NINH")
# ========================================================
def ap_dung_giao_dien():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root{
        --bg:#0a0e14;
        --surface:#11151c;
        --surface-2:#161b24;
        --border:#222a37;
        --text-primary:#e6edf3;
        --text-secondary:#8b96a5;
        --text-muted:#5b6573;
        --accent:#2dd4bf;
        --critical:#f85149;
        --warning:#d29922;
        --success:#3fb950;
        --radius:14px;
        --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.25);
    }

    html, body, [class^="css"], [class*=" css"]{
        font-family:'Inter', sans-serif;
        color:var(--text-primary);
    }
    .stApp{ background:var(--bg); }

    h1, h2, h3, h4{
        font-family:'Space Grotesk', sans-serif !important;
        letter-spacing:-0.01em;
    }

    /* Sidebar */
    section[data-testid="stSidebar"]{
        background:var(--surface);
        border-right:1px solid var(--border);
    }
    section[data-testid="stSidebar"] h3{
        color:var(--text-secondary);
        font-size:12px;
        text-transform:uppercase;
        letter-spacing:.08em;
        font-family:'Inter', sans-serif !important;
        font-weight:600;
    }

    /* Nút bấm */
    .stButton>button{
        border-radius:10px;
        font-weight:600;
        border:1px solid var(--border);
        transition:all .15s ease;
    }
    .stButton>button:hover{
        border-color:var(--accent);
        color:var(--accent);
    }
    .stButton>button:focus-visible{
        outline:2px solid var(--accent);
        outline-offset:2px;
    }

    /* Khung viền (container border=True) dùng cho thẻ đăng nhập */
    [data-testid="stVerticalBlockBorderWrapper"]{
        border-radius:var(--radius) !important;
        background:var(--surface) !important;
        border:1px solid var(--border) !important;
        box-shadow:var(--shadow);
    }

    /* Input chữ & mật khẩu */
    .stTextInput input{
        border-radius:10px !important;
        font-family:'JetBrains Mono', monospace !important;
        background:var(--surface-2) !important;
        border:1px solid var(--border) !important;
        color:var(--text-primary) !important;
    }

    /* Hộp thông báo */
    div[data-testid="stAlert"]{
        border-radius:10px;
        font-size:14px;
    }

    /* Chấm trạng thái nhấp nháy - biểu trưng giám sát thời gian thực */
    .live-dot{
        width:9px; height:9px; border-radius:50%;
        display:inline-block; margin-right:8px; vertical-align:middle;
    }
    .live-dot.on{
        background:var(--success);
        animation:nhip-dap 1.8s infinite;
    }
    .live-dot.off{ background:var(--text-muted); }
    @keyframes nhip-dap{
        0%{ box-shadow:0 0 0 0 rgba(63,185,80,.55); }
        70%{ box-shadow:0 0 0 7px rgba(63,185,80,0); }
        100%{ box-shadow:0 0 0 0 rgba(63,185,80,0); }
    }
    @media (prefers-reduced-motion: reduce){
        .live-dot.on{ animation:none; }
    }

    /* Băng tiêu đề trang điều hành */
    .bang-dieu-huong{
        background:linear-gradient(135deg, #11304a, #0a1a2e);
        border:1px solid var(--border);
        border-radius:var(--radius);
        padding:26px 30px;
        margin-bottom:26px;
        box-shadow:var(--shadow);
        display:flex;
        align-items:center;
        justify-content:space-between;
        flex-wrap:wrap;
        gap:16px;
    }
    .bang-dieu-huong h1{
        color:#fff; margin:0; font-size:26px; font-weight:700;
    }
    .bang-dieu-huong p{
        color:rgba(230,237,243,.65); margin:6px 0 0; font-size:13.5px;
    }
    .trang-thai-pill{
        font-family:'JetBrains Mono', monospace;
        font-size:12px;
        font-weight:600;
        padding:7px 14px;
        border-radius:999px;
        background:rgba(255,255,255,.06);
        border:1px solid rgba(255,255,255,.12);
        color:var(--text-primary);
        white-space:nowrap;
    }

    /* Thẻ số liệu thống kê */
    .the-so-lieu{
        background:var(--surface);
        border:1px solid var(--border);
        border-top:3px solid var(--accent-card, var(--accent));
        border-radius:var(--radius);
        padding:18px 20px;
        box-shadow:var(--shadow);
        height:100%;
    }
    .the-so-lieu .icon{ font-size:20px; margin-bottom:8px; }
    .the-so-lieu .nhan{
        color:var(--text-secondary); font-size:12.5px; font-weight:600;
        text-transform:uppercase; letter-spacing:.05em;
    }
    .the-so-lieu .gia-tri{
        font-family:'Space Grotesk', sans-serif;
        font-size:34px; font-weight:700; color:var(--text-primary);
        margin-top:4px;
    }

    /* Thanh công cụ lọc audit log */
    .tieu-de-khu{
        display:flex; align-items:center; justify-content:space-between;
        margin:8px 0 14px;
    }

    /* Thẻ log vi phạm */
    .the-log{
        background:var(--surface);
        border:1px solid var(--border);
        border-left:4px solid var(--text-muted);
        border-radius:12px;
        padding:16px 18px;
        margin-bottom:12px;
        box-shadow:var(--shadow);
    }
    .the-log.critical{ border-left-color:var(--critical); }
    .the-log.warning{ border-left-color:var(--warning); }
    .the-log .dong-tren{
        display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;
    }
    .the-log .ten-file{
        font-family:'JetBrains Mono', monospace; font-weight:600; font-size:14.5px;
        color:var(--text-primary);
    }
    .the-log .nhan-muc-do{
        font-family:'JetBrains Mono', monospace;
        font-size:11px; font-weight:700; letter-spacing:.04em;
        padding:3px 11px; border-radius:999px;
    }
    .the-log .nhan-muc-do.critical{ background:rgba(248,81,73,.14); color:var(--critical); }
    .the-log .nhan-muc-do.warning{ background:rgba(210,153,34,.14); color:var(--warning); }
    .the-log .vi-pham{ margin:10px 0 8px; }
    .pill{
        display:inline-block;
        background:rgba(45,212,191,.10);
        color:var(--accent);
        border:1px solid rgba(45,212,191,.25);
        border-radius:999px;
        padding:3px 11px;
        font-size:12px;
        font-weight:500;
        margin:2px 6px 2px 0;
    }
    .the-log .dong-duoi{
        display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;
        margin-top:8px; color:var(--text-secondary); font-size:12px;
    }
    .the-log .trang-thai-xl{
        font-family:'JetBrains Mono', monospace;
        background:var(--surface-2);
        border:1px solid var(--border);
        padding:2px 9px; border-radius:6px; color:var(--text-secondary);
    }

    /* Trạng thái rỗng */
    .trang-rong{
        text-align:center;
        padding:64px 20px;
        color:var(--text-secondary);
        background:var(--surface);
        border:1px dashed var(--border);
        border-radius:var(--radius);
    }
    .trang-rong .icon{ font-size:38px; margin-bottom:10px; }

    /* Khối đăng nhập */
    .khoi-icon-dang-nhap{
        text-align:center; font-size:38px; margin-bottom:6px;
    }
    .phu-de-dang-nhap{
        text-align:center; color:var(--text-secondary); font-size:13px;
        margin-top:-4px; margin-bottom:18px;
    }

    footer{ visibility:hidden; }
    .chan-trang{
        text-align:center; color:var(--text-muted); font-size:12px;
        font-family:'JetBrains Mono', monospace; margin-top:28px;
    }
    </style>
    """, unsafe_allow_html=True)

ap_dung_giao_dien()

# ========================================================
# 3. BỘ ĐIỀU PHỐI LOGIC WATCHDOG & PHÂN TÍCH LỖI
# ========================================================
def ghi_nhat_ky_log_json(ten_file, cac_loi, muc_do):
    ten_file_log = "dlp_history.json"
    ban_ghi_moi = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_name": ten_file,
        "violations": cac_loi,
        "severity_level": muc_do,
        "status": "WEB_INTERFACE_TRAVERSED_AND_FIXED"
    }
    danh_sach_log = []
    if os.path.exists(ten_file_log):
        try:
            with open(ten_file_log, "r", encoding="utf-8") as f:
                danh_sach_log = json.load(f)
        except Exception: pass
    danh_sach_log.append(ban_ghi_moi)
    with open(ten_file_log, "w", encoding="utf-8") as f:
        json.dump(danh_sach_log, f, ensure_ascii=False, indent=4)

def gui_canh_bao_discord(ten_file, loai_loi, muc_do):
    if "DÁN_LINK" in DISCORD_WEBHOOK_URL or not DISCORD_WEBHOOK_URL: return
    ma_mau = 15158332 if muc_do == "CRITICAL" else 15105570
    payload = {
        "embeds": [
            {
                "title": f" [DLP DEVSECOPS ALERT] PHÁT HIỆN RÒ RỈ CẤU CẤU TRÚC!",
                "color": ma_mau, 
                "fields": [
                    {"name": " Tệp cấu hình:", "value": f"`{ten_file}`", "inline": False},
                    {"name": " Thành phần rò rỉ:", "value": f"**{loai_loi}**", "inline": False},
                    {"name": " Mức độ nghiêm trọng:", "value": f"`{muc_do}`", "inline": True},
                    {"name": " Hành động:", "value": "Đã kích hoạt JSON AST Parser và đè cấu trúc bảo mật thành công!", "inline": False}
                ],
                "footer": {"text": "Hệ thống DLP Giám sát cấu trúc nguồn thời gian thực v3.0 Pro"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        ]
    }
    try: requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception: pass

def gui_otp_qua_discord_bot(ma_otp):
    """Giả lập luồng Gateway: Quét Zalo xong hệ thống đẩy OTP về thiết bị di động của Admin"""
    if "DÁN_LINK" in DISCORD_WEBHOOK_URL or not DISCORD_WEBHOOK_URL: return
    payload = {
        "embeds": [
            {
                "title": "  MÃ XÁC THỰC HỆ THỐNG",
                "description": f"Thiết bị di động vừa quét mã định danh Zalo thành công.\n\n🔑 Mã OTP của bạn là: **{ma_otp}**\n*(Mã có hiệu lực trong vòng 2 phút)*",
                "color": 26419,
                "footer": {"text": "An ninh cổng bảo mật BMUDHT 2FA"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        ]
    }
    try: requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception: pass

def quat_va_xu_ly_file(duong_dan_file):
    ten_file_ngan = os.path.basename(duong_dan_file)
    if ten_file_ngan in ["main.py", "dlp_engine.py", "van_ban_AN_TOAN.txt", "dlp_history.json", "app.py", "bao_mat_2fa.py", "dlp_2fa_secret.txt", "qrcode_2fa.png", "zalo_otp_cache.json"]: return

    if ten_file_ngan.endswith('.json'):
        try:
            with open(duong_dan_file, "r", encoding="utf-8") as f:
                du_lieu_json = json.load(f)
        except Exception: return

        cac_loi_phat_hien = []
        dlp_engine.quat_cau_truc_json(du_lieu_json, cac_loi_phat_hien)

        if cac_loi_phat_hien:
            dlp_engine.che_mo_cau_truc_json(du_lieu_json)
            with open(duong_dan_file, "w", encoding="utf-8") as f:
                json.dump(du_lieu_json, f, ensure_ascii=False, indent=4)
            
            ghi_nhat_ky_log_json(ten_file_ngan, cac_loi_phat_hien, "CRITICAL")
            gui_canh_bao_discord(ten_file_ngan, ", ".join(cac_loi_phat_hien), "CRITICAL")
        return

    try:
        with open(duong_dan_file, "r", encoding="utf-8") as f: noidung = f.read()
    except Exception: return

    emails = dlp_engine.quat_tim_email(noidung)
    sdts = dlp_engine.quat_tim_sdt(noidung)
    thes = dlp_engine.quat_tim_the_tin_dung(noidung)
    opena_keys = dlp_engine.quat_tim_openai_key(noidung)

    cac_loi_phat_hien = []
    muc_do = "WARNING"
    if emails: cac_loi_phat_hien.append("Email cá nhân")
    if sdts: cac_loi_phat_hien.append("Số điện thoại khách hàng")
    if thes: 
        cac_loi_phat_hien.append("Số thẻ tín dụng")
        muc_do = "CRITICAL"
    if opena_keys: 
        cac_loi_phat_hien.append("OpenAI API Key")
        muc_do = "CRITICAL"

    if cac_loi_phat_hien:
        noidung_da_sua = dlp_engine.che_mo_email(noidung)
        noidung_da_sua = dlp_engine.che_mo_sdt(noidung_da_sua)
        noidung_da_sua = dlp_engine.che_mo_the_tin_dung(noidung_da_sua)
        noidung_da_sua = dlp_engine.che_mo_openai_key(noidung_da_sua)

        if ten_file_ngan in ["test.txt", "kiem_tra.txt"]:
            with open("van_ban_AN_TOAN.txt", "w", encoding="utf-8") as f_out: f_out.write(noidung_da_sua)
        else:
            with open(duong_dan_file, "w", encoding="utf-8") as f_out: f_out.write(noidung_da_sua)
            
        ghi_nhat_ky_log_json(ten_file_ngan, cac_loi_phat_hien, muc_do)
        gui_canh_bao_discord(ten_file_ngan, ", ".join(cac_loi_phat_hien), muc_do)

class ThaoTacFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory: quat_va_xu_ly_file(event.src_path)
    def on_created(self, event):
        if not event.is_directory: quat_va_xu_ly_file(event.src_path)

def chay_ngam_watchdog():
    path = "."
    event_handler = ThaoTacFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    return observer

# ========================================================
# 4. CÁC HÀM HỖ TRỢ HIỂN THỊ (UI COMPONENTS)
# ========================================================
def ve_the_so_lieu(icon, nhan, gia_tri, mau_accent):
    st.markdown(f"""
    <div class="the-so-lieu" style="--accent-card:{mau_accent}">
        <div class="icon">{icon}</div>
        <div class="nhan">{nhan}</div>
        <div class="gia-tri">{gia_tri}</div>
    </div>
    """, unsafe_allow_html=True)

def ve_the_log(log):
    muc_do = log.get("severity_level", "WARNING")
    lop_css = "critical" if muc_do == "CRITICAL" else "warning"
    danh_sach_pill = "".join(
        f'<span class="pill">{v}</span>' for v in log.get("violations", [])
    )
    st.markdown(f"""
    <div class="the-log {lop_css}">
        <div class="dong-tren">
            <span class="ten-file"> {log.get('file_name')}</span>
            <span class="nhan-muc-do {lop_css}">{muc_do}</span>
        </div>
        <div class="vi-pham">{danh_sach_pill}</div>
        <div class="dong-duoi">
            <span class="trang-thai-xl">{log.get('status')}</span>
            <span>⏱ {log.get('timestamp')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========================================================
# 5. CHƯƠNG TRÌNH ĐIỀU HƯỚNG GIAO DIỆN WEB (UI MAIN FLOW)
# ========================================================

# --- LỚP BẢO MẬT 1: ĐĂNG NHẬP MẬT KHẨU CỐ ĐỊNH ---
if not st.session_state.lop_1_thanh_cong:
    st.markdown("<h1 style='text-align: center; margin-top:40px;'>🛡️ HỆ THỐNG CỔNG BẢO MẬT DLP</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b96a5;'>LỚP 1 / 2 · XÁC THỰC TÀI KHOẢN QUẢN TRỊ VIÊN</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<div class='khoi-icon-dang-nhap'>🔐</div>", unsafe_allow_html=True)
            st.markdown("<p class='phu-de-dang-nhap'>Nhập thông tin quản trị để mở khóa cổng bảo mật</p>", unsafe_allow_html=True)
            with st.form("form_dang_nhap_lop_1"):
                tai_khoan = st.text_input(" Tên tài khoản Admin:", value="admin")
                mat_khau = st.text_input(" Mật khẩu hệ thống:", type="password")
                nut_dang_nhap = st.form_submit_button("TIẾP TỤC ➔", use_container_width=True)

                if nut_dang_nhap:
                    if tai_khoan == "admin" and mat_khau == "admin123":
                        st.session_state.lop_1_thanh_cong = True
                        # Tạo luôn mã QR Zalo ban đầu cho lớp 2
                        st.session_state.ma_otp_zalo = bao_mat_2fa.khoi_tao_he_thong_zalo_2fa()
                        gui_otp_qua_discord_bot(st.session_state.ma_otp_zalo)
                        st.success("🟩 Mật khẩu chính xác! Đang tạo cổng kết nối QR...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("🟥 Tài khoản hoặc Mật khẩu không chính xác!")

# --- LỚP BẢO MẬT 2: ĐĂNG NHẬP BIẾN THỂ ZALO QR CODE ---
elif st.session_state.lop_1_thanh_cong and not st.session_state.lop_2_thanh_cong:
    st.markdown("<h1 style='text-align: center; margin-top:40px;'> XÁC THỰC QUA ỨNG DỤNG</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b96a5;'>LỚP 2 / 2 · QUÉT MÃ QR ĐỂ NHẬN MÃ OTP VỀ ĐIỆN THOẠI</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            if st.button("🔄 Đổi mã QR mới", use_container_width=True):
                st.session_state.ma_otp_zalo = bao_mat_2fa.khoi_tao_he_thong_zalo_2fa()
                gui_otp_qua_discord_bot(st.session_state.ma_otp_zalo)
                st.rerun()

            if os.path.exists("qrcode_2fa.png"):
                st.image("qrcode_2fa.png", caption="MÃ QR ĐỊNH DANH", use_container_width=True)

            ma_otp = st.text_input("🔢 Nhập mã OTP 6 số nhận được:", max_chars=6, type="password")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔒 XÁC MINH & VÀO DASHBOARD", use_container_width=True):
                    if bao_mat_2fa.xac_thuc_ma_zalo_otp(ma_otp):
                        st.session_state.lop_2_thanh_cong = True
                        st.success("🟩 Xác thực Zalo thành công! Đang mở Dashboard...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("🟥 Mã OTP Zalo không chính xác hoặc đã hết hạn!")
            with c2:
                if st.button("⬅ Quay lại", use_container_width=True):
                    st.session_state.lop_1_thanh_cong = False
                    st.rerun()

# --- MÀN HÌNH CHÍNH 3: TRUNG TÂM QUẢN TRỊ TRÊN WEB ---
else:
    with st.sidebar:
        st.markdown("<div style='font-size:26px;'>🛡️</div>", unsafe_allow_html=True)
        st.markdown("### Quản trị hệ thống")
        st.success("🟢 Tài khoản: admin")
        st.markdown("---")

        che_do_giam_sat = st.toggle(" Kích hoạt Giám sát Thời gian thực", value=True)

        if che_do_giam_sat:
            st.info(" Tháp giám sát đang theo dõi ngầm trong thư mục...")
            if st.session_state.observer_instance is None:
                st.session_state.observer_instance = chay_ngam_watchdog()
        else:
            st.warning("🛑 Trạng thái: Dừng giám sát ngầm.")
            if st.session_state.observer_instance is not None:
                st.session_state.observer_instance.stop()
                st.session_state.observer_instance.join()
                st.session_state.observer_instance = None

        st.markdown("---")
        if st.button("🚪 ĐĂNG XUẤT (KHÓA HỆ THỐNG)", use_container_width=True):
            if st.session_state.observer_instance is not None:
                st.session_state.observer_instance.stop()
                st.session_state.observer_instance = None
            st.session_state.lop_1_thanh_cong = False
            st.session_state.lop_2_thanh_cong = False
            st.rerun()

    trang_thai_dot = "on" if che_do_giam_sat else "off"
    trang_thai_text = "ĐANG GIÁM SÁT" if che_do_giam_sat else "TẠM DỪNG"
    st.markdown(f"""
    <div class="bang-dieu-huong">
        <div>
            <h1>🛡️ Trung tâm Giám sát An toàn Thông tin (DLP)</h1>
            <p>Tự động phát hiện &amp; che dấu dữ liệu nhạy cảm trong thư mục theo thời gian thực</p>
        </div>
        <div class="trang-thai-pill">
            <span class="live-dot {trang_thai_dot}"></span>{trang_thai_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    file_log = "dlp_history.json"
    du_lieu_log = []
    tong_su_co, so_critical, so_warning = 0, 0, 0

    if os.path.exists(file_log):
        try:
            with open(file_log, "r", encoding="utf-8") as f:
                du_lieu_log = json.load(f)
                tong_su_co = len(du_lieu_log)
                so_critical = sum(1 for item in du_lieu_log if item.get("severity_level") == "CRITICAL")
                so_warning = sum(1 for item in du_lieu_log if item.get("severity_level") == "WARNING")
        except Exception: pass

    m1, m2, m3 = st.columns(3)
    with m1: ve_the_so_lieu("📦", "Tổng file rò rỉ được vá sạch", tong_su_co, "#2dd4bf")
    with m2: ve_the_so_lieu("🔴", "Nguy cơ cao (CRITICAL)", so_critical, "#f85149")
    with m3: ve_the_so_lieu("🟠", "Nguy cơ thấp (WARNING)", so_warning, "#d29922")

    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)

    tieu_de_col, loc_col, tim_col = st.columns([2.2, 1, 1.4])
    with tieu_de_col:
        st.markdown("### 📋 Chi tiết lịch sử Audit Log hệ thống")
    with loc_col:
        loc_muc_do = st.selectbox("Mức độ", ["Tất cả", "CRITICAL", "WARNING"], label_visibility="collapsed")
    with tim_col:
        tim_ten_file = st.text_input("Tìm tên file", placeholder="🔎 Tìm theo tên file...", label_visibility="collapsed")

    danh_sach_hien_thi = list(reversed(du_lieu_log))
    if loc_muc_do != "Tất cả":
        danh_sach_hien_thi = [l for l in danh_sach_hien_thi if l.get("severity_level") == loc_muc_do]
    if tim_ten_file:
        danh_sach_hien_thi = [l for l in danh_sach_hien_thi if tim_ten_file.lower() in l.get("file_name", "").lower()]

    if not du_lieu_log:
        st.markdown("""
        <div class="trang-rong">
            <div class="icon">✨</div>
            <div>Thư mục an toàn. Chưa phát hiện hành vi vi phạm.</div>
        </div>
        """, unsafe_allow_html=True)
    elif not danh_sach_hien_thi:
        st.markdown("""
        <div class="trang-rong">
            <div class="icon">🔍</div>
            <div>Không tìm thấy bản ghi phù hợp với bộ lọc hiện tại.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for log in danh_sach_hien_thi:
            ve_the_log(log)

    st.markdown(f"<div class='chan-trang'>{PHIEN_BAN_HE_THONG} · Cập nhật mỗi 5 giây</div>", unsafe_allow_html=True)

    if che_do_giam_sat:
        time.sleep(5)
        st.rerun()
