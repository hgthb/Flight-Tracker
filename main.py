import requests
import time
import datetime
import firebase_admin
from firebase_admin import credentials, db

# --- ID CỐ ĐỊNH: KẾT NỐI FIREBASE ---
# Lưu ý: File serviceAccountKey.json phải nằm cùng thư mục với file này trên PythonAnywhere
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://pleiku-flight-radar-default-rtdb.asia-southeast1.firebasedatabase.app'
        })
        print("✅ Kết nối Firebase thành công.")
    except Exception as e:
        print(f"❌ Lỗi kết nối Firebase: {e}")

def fetch_flight_data():
    now = datetime.datetime.now()
    # URL lấy dữ liệu sân bay Pleiku (PXU)
    url = f"https://api.flightradar24.com/common/v1/airport.json?code=pxu&plugin[]=&plugin-setting[schedule][mode]=&plugin-setting[schedule][timestamp]={int(time.time())}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        schedule = data['result']['response']['airport']['pluginData']['schedule']
        
        flights_to_process = []
        if 'arrivals' in schedule:
            for f in schedule['arrivals']['data']: flights_to_process.append({'f': f, 'type': 'arr'})
        if 'departures' in schedule:
            for f in schedule['departures']['data']: flights_to_process.append({'f': f, 'type': 'dep'})

        for item in flights_to_process:
            f = item['f']['flight']
            t = f['time']
            
            # Hàm phụ chuyển đổi Timestamp thành HH:mm
            def fmt_time(ts):
                return datetime.datetime.fromtimestamp(ts).strftime("%H:%M") if ts else "--:--"

            # Trích xuất 7 thông tin cốt lõi theo yêu cầu của anh Hưng
            payload = {
                "flight": f['identification']['number']['default'] or "N/A", # 1. Số hiệu chuyến bay
                "reg": f['aircraft'].get('registration') or "N/A",           # 2. Số Aircraft Reg
                "origin_icao": f['airport']['origin']['code']['icao'] or "----", # 3a. Sân bay đi (ICAO)
                "dest_icao": f['airport']['destination']['code']['icao'] or "----", # 3b. Sân bay đến (ICAO)
                
                # 4 & 5. Giờ cất cánh (Kế hoạch & Thực tế)
                "dep_sched": fmt_time(t['scheduled']['departure']),
                "dep_real": fmt_time(t['real']['departure'] or t['estimated']['departure']),
                
                # 6 & 7. Giờ hạ cánh (Kế hoạch & Thực tế)
                "arr_sched": fmt_time(t['scheduled']['arrival']),
                "arr_real": fmt_time(t['real']['arrival'] or t['estimated']['arrival']),
                
                "status": f['status']['text'],
                "raw_sort_time": t['scheduled']['departure'] if item['type'] == 'dep' else t['scheduled']['arrival']
            }

            # Lưu vào Firebase: Tên node kết hợp Số hiệu và Ngày để không bị ghi đè dữ liệu cũ
            node_name = f"{payload['flight']}_{now.strftime('%Y%m%d')}"
            db.reference(f"flight_logs/{node_name}").update(payload)
            
        print(f"🚀 Cập nhật thành công {len(flights_to_process)} chuyến bay vào lúc {now.strftime('%H:%M:%S')}")

    except Exception as e:
        print(f"❌ Lỗi khi lấy dữ liệu: {e}")

if __name__ == "__main__":
    while True:
        fetch_flight_data()
        # Nghỉ theo tần suất (mặc định 2 phút)
        try:
            tan_suat = db.reference('CAI_DAT/tan_suat').get()
            time.sleep(int(tan_suat or 2) * 60)
        except:
            time.sleep(120)
