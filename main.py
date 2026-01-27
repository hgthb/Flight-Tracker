import requests
from datetime import datetime, timedelta

# ==========================================
# VERSION: A.20
# DESCRIPTION: Bản cưỡng bức đồng bộ Terminal & Sửa lỗi lệch -7h
# ==========================================

# Dòng này để anh kiểm tra ngay lập tức xem đã nhận bản mới chưa
print("\n" + "📡 " + "═"*45)
print("   HỆ THỐNG TRA CỨU HÀNG KHÔNG - PHIÊN BẢN A.20")
print("   TRẠNG THÁI: ĐÃ ĐỒNG BỘ TRỰC TIẾP")
print("📡 " + "═"*45 + "\n")

class PleikuFlightRadar:
    def __init__(self):
        # API Key của anh Hưng
        self.api_key = "cba47be516a88ec3301d9f54f28b5d7e"
        self.url = "http://api.aviationstack.com/v1/flights"

    def fetch_flight(self, iata_code):
        params = {'access_key': self.api_key, 'flight_iata': iata_code}
        try:
            r = requests.get(self.url, params=params)
            data = r.json()
            
            if not data or 'data' not in data or len(data['data']) == 0:
                return f"⚠️ Không tìm thấy dữ liệu cho chuyến {iata_code}."
            
            f = data['data'][0]
            
            def fix_vietnam_time(time_str):
                if not time_str: return "N/A"
                try:
                    # Dữ liệu từ API đang bị cộng dư 7 tiếng, chúng ta trừ lại
                    dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    dt_fixed = dt - timedelta(hours=7)
                    return dt_fixed.strftime("%H:%M ngày %d/%m/%Y")
                except:
                    return time_str

            return (f"✅ THÔNG TIN CHUYẾN BAY: {f['flight']['iata']}\n"
                    f"──────────────────────────────────────────\n"
                    f"✈ Số đăng ký (Reg): {f['aircraft'].get('registration') if f.get('aircraft') else 'N/A'}\n"
                    f"✈ Trạng thái: {f['flight_status'].upper()}\n"
                    f"✈ Lộ trình: {f['departure']['iata']} ✈ {f['arrival']['iata']}\n"
                    f"✈ Giờ cất cánh (Đã fix): {fix_vietnam_time(f['departure'].get('scheduled'))}\n"
                    f"✈ Giờ hạ cánh (Đã fix): {fix_vietnam_time(f['arrival'].get('scheduled'))}\n"
                    f"✈ Nhà ga (Đi/Đến): T{f['departure'].get('terminal') or '-'} / T{f['arrival'].get('terminal') or '-'}\n"
                    f"✈ Cổng (Đi/Đến): {f['departure'].get('gate') or '-'} / {f['arrival'].get('gate') or '-'}\n"
                    f"──────────────────────────────────────────")
        except Exception as e:
            return f"❌ Lỗi: {e}"

if __name__ == "__main__":
    radar = PleikuFlightRadar()
    code = input("✈ Nhập số hiệu chuyến bay (VD: VN1422): ").strip().upper()
    if code:
        print(radar.fetch_flight(code))
