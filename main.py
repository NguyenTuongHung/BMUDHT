import dlp_engine
import os
import time
import requests
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DISCORD_WEBHOOK_URL = "DÁN_LINK_WEBHOOK_DISCORD_CỦA_BẠN_VÀO_ĐÂY"

def ghi_nhat_ky_log_json(ten_file, cac_loi, muc_do):
    ten_file_log = "dlp_history.json"
    ban_ghi_moi = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_name": ten_file,
        "violations": cac_loi,
        "severity_level": muc_do,
        "status": "STRUCTURE_PARSED_AND_FIXED"
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
                "title": f"🚨 [DLP DEVSECOPS ALERT] PHÁT HIỆN RÒ RỈ CẤU CẤU TRÚC!",
                "color": ma_mau, 
                "fields": [
                    {"name": "📁 Tệp cấu hình:", "value": f"`{ten_file}`", "inline": False},
                    {"name": "⚠️ Thành phần rò rỉ:", "value": f"**{loai_loi}**", "inline": False},
                    {"name": "📊 Mức độ nghiêm trọng:", "value": f"`{muc_do}`", "inline": True},
                    {"name": "🛠️ Hành động:", "value": "Đã kích hoạt JSON AST Parser và đè cấu trúc bảo mật thành công!", "inline": False}
                ],
                "footer": {"text": "Hệ thống DLP Giám sát cấu trúc nguồn thời gian thực v3.0 Pro"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        ]
    }
    try: requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception: pass

def quat_va_xu_ly_file(duong_dan_file):
    ten_file_ngan = os.path.basename(duong_dan_file)
    if ten_file_ngan in ["main.py", "dlp_engine.py", "van_ban_AN_TOAN.txt", "dlp_history.json"]: return

    # --- NHÁNH XỬ LÝ 1: NẾU LÀ FILE CẤU TRÚC JSON ---
    if ten_file_ngan.endswith('.json'):
        try:
            with open(duong_dan_file, "r", encoding="utf-8") as f:
                du_lieu_json = json.load(f)
        except Exception: return # Bỏ qua nếu file JSON viết sai cú pháp chưa phân tích được

        cac_loi_phat_hien = []
        dlp_engine.quat_cau_truc_json(du_lieu_json, cac_loi_phat_hien)

        if cac_loi_phat_hien:
            print(f"\n[🚨 DEVSECOPS ALERT] PHÁT HIỆN KHÓA BẢO MẬT TRONG FILE JSON: {ten_file_ngan}")
            print(f"    Chi tiết: {', '.join(cac_loi_phat_hien)}")
            
            # Thực hiện vá trực tiếp cấu trúc
            dlp_engine.che_mo_cau_truc_json(du_lieu_json)
            with open(duong_dan_file, "w", encoding="utf-8") as f:
                json.dump(du_lieu_json, f, ensure_ascii=False, indent=4)
            print(f"    -> [THÀNH CÔNG] Đã băm rỗng các trường mật khẩu trong file {ten_file_ngan}!")
            
            ghi_nhat_ky_log_json(ten_file_ngan, cac_loi_phat_hien, "CRITICAL")
            gui_canh_bao_discord(ten_file_ngan, ", ".join(cac_loi_phat_hien), "CRITICAL")
        return

    # --- NHÁNH XỬ LÝ 2: CÁC FILE VĂN BẢN THÔ (TXT, LOG,...) NHƯ CŨ ---
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
        print(f"\n[!] PHÁT HIỆN VI PHẠM TẠI FILE VĂN BẢN: {ten_file_ngan}")
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

if __name__ == "__main__":
    print("==================================================")
    print("   HỆ THỐNG DLP GIÁM SÁT ĐA CẤU TRÚC THỜI GIAN THỰC ")
    print("==================================================")
    print("[*] Trạng thái: Bộ phân tích JSON Parser sẵn sàng...")
    print("[*] Đang giám sát cả File văn bản (.txt) và File cấu hình (.json)...")
    print("==================================================")
    path = "."
    event_handler = ThaoTacFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: observer.stop()
    observer.join()