import requests
from datetime import datetime, timedelta

# ==========================================
# VERSION: A.16
# DESCRIPTION: Hiệu chỉnh trừ 7 tiếng để khớp với giờ thực tế Việt Nam
# ==========================================

print("\n" + "🚀 " + "═"*45)
print("   HỆ THỐNG TRA CỨU HÀNG KHÔNG - PHIÊN BẢN A.16")
print("   TRẠNG THÁI: ĐÃ FIX LỖI LỆCH 7 TIẾNG")
print("🚀 " + "═"*45 + "\n")

class PleikuFlightRadar:
    def __init__(self):
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
            
            # HÀM XỬ LÝ GIỜ: Trừ đi 7 tiếng để về đúng giờ Việt Nam
            def fix_vietnam_time(time_str):
                if not time_str: return "N/A"
                try:
                    # Chuyển đổi chuỗi ISO thành datetime
                    dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    # TRỪ ĐI 7 TIẾNG để sửa lỗi hiển thị sai của API
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
                    f"✈ Nhà ga (Ga đi/Ga đến): T{f['departure'].get('terminal') or '-'} / T{f['arrival'].get('terminal') or '-'}\n"
                    f"✈ Cổng (Gate đi/Gate đến): {f['departure'].get('gate') or '-'} / {f['arrival'].get('gate') or '-'}\n"
                    f"──────────────────────────────────────────")
        except Exception as e:
            return f"❌ Lỗi kết nối: {e}"

if __name__ == "__main__":
    radar = PleikuFlightRadar()
    code = input("✈ Nhập số hiệu chuyến bay (VD: VN1422): ").strip().upper()
    if code:
        print(radar.fetch_flight(code))
