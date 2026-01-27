import os
import sys

# Tự động cài đặt thư viện requests nếu thiếu
try:
    import requests
except ImportError:
    print("...Đang chuẩn bị thư viện kết nối (requests)...")
    os.system('pip install requests')
    import requests

from datetime import datetime, timedelta

# ==========================================
# VERSION: A.13
# DESCRIPTION: Bản tự hành (Self-running) cho GitHub Codespaces
# ==========================================

print("\n" + "="*50)
print("   HỆ THỐNG TRA CỨU CHUYẾN BAY - PHIÊN BẢN A.13")
print("   TRẠNG THÁI: ĐÃ SẴN SÀNG")
print("="*50 + "\n")

class FlightApp:
    def __init__(self):
        self.api_key = "cba47be516a88ec3301d9f54f28b5d7e"
        self.url = "http://api.aviationstack.com/v1/flights"

    def get_data(self, flight_no):
        params = {'access_key': self.api_key, 'flight_iata': flight_no}
        try:
            print(f"📡 Đang truy vấn dữ liệu từ vệ tinh cho chuyến: {flight_no}...")
            r = requests.get(self.url, params=params)
            data = r.json()

            if not data or 'data' not in data or len(data['data']) == 0:
                return "❌ Không tìm thấy thông tin. Có thể chuyến bay chưa được cấp phép hoặc sai số hiệu."

            f = data['data'][0]
            
            # Xử lý giờ địa phương (GMT+7)
            raw_time = f['departure'].get('scheduled')
            vn_time = "N/A"
            if raw_time:
                dt = datetime.fromisoformat(raw_time.replace('Z', '+00:00')) + timedelta(hours=7)
                vn_time = dt.strftime("%H:%M ngày %d/%m/%Y")

            return (f"\n✈ THÔNG TIN CHUYẾN BAY: {f['flight']['iata']}\n"
                    f"──────────────────────────────────────────\n"
                    f"▶ Số đăng ký tàu bay: {f['aircraft'].get('registration') if f.get('aircraft') else 'Chưa cập nhật'}\n"
                    f"▶ Tình trạng thực tế: {f.get('flight_status', 'N/A').upper()}\n"
                    f"▶ Lộ trình: {f['departure'].get('iata')} ✈ {f['arrival'].get('iata')}\n"
                    f"▶ Giờ cất cánh (VN): {vn_time}\n"
                    f"▶ Nhà ga/Cổng đi: T{f['departure'].get('terminal') or '-'} / G{f['departure'].get('gate') or '-'}\n"
                    f"▶ Nhà ga/Cổng đến: T{f['arrival'].get('terminal') or '-'} / G{f['arrival'].get('gate') or '-'}\n"
                    f"──────────────────────────────────────────")
        except Exception as e:
            return f"❌ Lỗi kết nối: {str(e)}"

if __name__ == "__main__":
    app = FlightApp()
    f_code = input("👉 Nhập số hiệu chuyến bay (VD: VJ392): ").strip().upper()
    if f_code:
        print(app.get_data(f_code))
    else:
        print("⚠ Anh chưa nhập số hiệu chuyến bay!")
