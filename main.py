import network
import urequests
import ujson
from machine import Pin, ADC
import time
import ntptime

# ==========================================
# 1. Hardware Setup
# ==========================================

# GP2Y1010 (Dust Sensor)
led_pin = Pin(32, Pin.OUT)       # สายสีเหลือง (LED) ต่อ Pin 32
dust_adc = ADC(Pin(35))          # สายสีเขียว (Vo) ต่อ Pin 35
dust_adc.atten(ADC.ATTN_11DB)
dust_adc.width(ADC.WIDTH_12BIT)

NO_DUST_VOLTAGE = 1.97
K_FACTOR = 170.0

# MQ-135 (Gas Sensor)
gas_adc = ADC(Pin(33))           # ขา AO ต่อ Pin 33 (ฝั่งซ้าย)
gas_adc.atten(ADC.ATTN_11DB)
gas_adc.width(ADC.WIDTH_12BIT)

# ==========================================
# 2. WiFi & NTP Setup
# ==========================================
wlan = network.WLAN(network.STA_IF)
wlan.active(False)
time.sleep(1)
wlan.active(True)
time.sleep(1)

print('Connecting to WiFi...')
wlan.connect('Z', '13052555')

timeout = 10
while not wlan.isconnected() and timeout > 0:
    print('.', end='')
    time.sleep(1)
    timeout -= 1

if wlan.isconnected():
    print('\nConnected to WiFi!')
    print('Network config:', wlan.ifconfig())
    try:
        ntptime.host = "pool.ntp.org"
        ntptime.settime()
        print("NTP Time Synced Successfully!")
    except Exception as e:
        print("NTP Sync Failed:", e)
else:
    print('\nWiFi Connection Failed!')

# ==========================================
# 3. NocoDB Configuration
# ==========================================
url = "https://noco.phukhieo.ac.th/api/v2/tables/mmo2nkzx4m7mc2d/records"
headers = {
    "accept": "application/json",
    "xc-token": "U3WjT_etA7hXLe2uFhVhFYvLppouR3-W--CqCnO8",
    "Content-Type": "application/json"
}

# ==========================================
# 4. Telegram Notification & PCD Standards
# ==========================================
# เกณฑ์มาตรฐานคุณภาพอากาศ PM 2.5 ประเทศไทย (กรมควบคุมมลพิษ PCD / สคพ.3)
# อ้างอิง: https://epo03.pcd.go.th/th/news/detail/178650
# 🔵 ระดับ 1 (สีฟ้า): 0.0 - 15.0 µg/m³   -> อากาศดีมาก (Very Good)
# 🟢 ระดับ 2 (สีเขียว): 15.1 - 25.0 µg/m³ -> อากาศดี (Good)
# 🟡 ระดับ 3 (สีเหลือง): 25.1 - 37.5 µg/m³ -> ปานกลาง (Moderate)
# 🟠 ระดับ 4 (สีส้ม): 37.6 - 75.0 µg/m³  -> เริ่มมีผลกระทบต่อสุขภาพ (Unhealthy for sensitive groups)
# 🔴 ระดับ 5 (สีแดง): 75.1 µg/m³ ขึ้นไป  -> มีผลกระทบต่อสุขภาพ (Hazardous)

TELEGRAM_BOT_TOKEN = "8974699444:AAHoVIXSNMiBa9h-PB1iyrQdlbBtPyOUJ2s"
TELEGRAM_CHAT_ID = "7903084332"
PM25_ALERT_THRESHOLD = 75.0                     # เกณฑ์แจ้งเตือน PM 2.5 (> 75.0 µg/m³ = ระดับสีแดง มีผลกระทบต่อสุขภาพ)
ALERT_COOLDOWN_SECONDS = 300                    # ระยะเวลาหน่วงการส่งแจ้งเตือนซ้ำ (300 วินาที = 5 นาที) เพื่อไม่ให้ส่งถี่เกินไป
last_alert_time = 0

# ==========================================
# 5. Helper Functions
# ==========================================

def get_iso_timestamp():
    t = time.gmtime()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}+00:00".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )

def read_dust_sensor():
    led_pin.value(0)
    time.sleep_us(280)
    raw_val = dust_adc.read()
    time.sleep_us(40)
    led_pin.value(1)
    time.sleep_us(9680)
    return raw_val

def get_smooth_dust(samples=10):
    total_raw = 0
    for _ in range(samples):
        total_raw += read_dust_sensor()
        time.sleep_ms(10)

    avg_raw = total_raw / samples
    voltage = avg_raw * (3.3 / 4095.0)

    dust_density = (voltage - NO_DUST_VOLTAGE) * K_FACTOR
    if dust_density < 0:
        dust_density = 0.0

    return round(dust_density, 2), round(voltage, 2)

def read_gas_sensor(samples=10):
    total_raw = 0
    for _ in range(samples):
        total_raw += gas_adc.read()
        time.sleep_ms(10)
    
    avg_raw = total_raw / samples
    gas_voltage = avg_raw * (3.3 / 4095.0)
    gas_ppm = (gas_voltage / 3.3) * 1000  
    
    if avg_raw > 2800:
        status = "detected"
    else:
        status = "normal"
        
    return status, round(avg_raw, 0), round(gas_voltage, 2), round(gas_ppm, 2)

def send_telegram_alert(pm25_val, gas_val, time_str, device_id="a1"):
    """ส่งข้อความแจ้งเตือนภาษาไทยไปยัง Telegram เมื่อ PM 2.5 เกินเกณฑ์ 75 µg/m³"""
    global last_alert_time
    
    # ตรวจสอบว่ามีการใส่ Token แล้วหรือยัง
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN" or TELEGRAM_CHAT_ID == "YOUR_TELEGRAM_CHAT_ID":
        print("[Telegram] ข้ามการส่ง: ยังไม่ได้ตั้งค่า TELEGRAM_BOT_TOKEN หรือ TELEGRAM_CHAT_ID")
        return
        
    current_ticks = time.time()
    if current_ticks - last_alert_time < ALERT_COOLDOWN_SECONDS:
        print("[Telegram] ข้ามการส่ง: อยู่ในช่วง Cooldown (เหลือ {} วินาที)".format(
            int(ALERT_COOLDOWN_SECONDS - (current_ticks - last_alert_time))
        ))
        return

    # ข้อความภาษาไทยแจ้งเตือนสถานการณ์วิกฤต
    message = (
        "🚨 <b>แจ้งเตือนคุณภาพอากาศวิกฤต!</b> 🚨\n\n"
        "⚠️ <b>ค่าฝุ่น PM 2.5 เกินมาตรฐานความปลอดภัย</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔴 <b>สถานะ:</b> มีผลกระทบต่อสุขภาพ (Hazardous)\n"
        "📊 <b>ค่า PM 2.5:</b> <code>{:.2f}</code> µg/m³ (เกณฑ์วิกฤต > 75.0)\n"
        "💨 <b>ระดับก๊าซ:</b> <code>{:.2f}</code> PPM\n"
        "📍 <b>อุปกรณ์:</b> {}\n"
        "🕒 <b>เวลาตรวจวัด:</b> {}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "😷 <b>คำแนะนำด้านสุขภาพ:</b>\n"
        "• หลีกเลี่ยงกิจกรรมกลางแจ้งทุกประเภท\n"
        "• ปิดประตูหน้าต่างให้มิดชิด และเปิดเครื่องฟอกอากาศ\n"
        "• สวมหน้ากากป้องกันฝุ่น N95 ทันทีเมื่อจำเป็นต้องออกนอกอาคาร"
    ).format(pm25_val, gas_val, device_id, time_str)

    telegram_url = "https://api.telegram.org/bot{}/sendMessage".format(TELEGRAM_BOT_TOKEN)
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        print("[Telegram] กำลังส่งการแจ้งเตือนไปยัง Telegram...")
        body_bytes = ujson.dumps(payload).encode('utf-8')
        tg_headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": str(len(body_bytes))
        }
        res = urequests.post(telegram_url, headers=tg_headers, data=body_bytes)
        if res.status_code == 200:
            print("[Telegram] ส่งแจ้งเตือนสำเร็จ!")
            last_alert_time = current_ticks
        else:
            print("[Telegram] ส่งไม่สำเร็จ Status Code:", res.status_code, "Response:", res.text)
        res.close()
    except Exception as e:
        print("[Telegram] Error:", e)

# ==========================================
# 6. Main Loop
# ==========================================
while True:
    dust_val, dust_volt = get_smooth_dust(samples=10)
    gas_status, gas_raw, gas_volt, gas_ppm = read_gas_sensor(samples=10)
    current_time = get_iso_timestamp()

    print("Timestamp:", current_time)
    print("ฝุ่น PM2.5: {} µg/m³ (แรงดัน: {:.2f}V)".format(dust_val, dust_volt))
    print("ก๊าซ MQ-135: Raw = {} | แรงดัน = {:.2f}V | PPM = {:.2f} ppm | สถานะ: {}".format(gas_raw, gas_volt, gas_ppm, gas_status))

    # ตรวจสอบเงื่อนไข PM2.5 > 75 µg/m³ เพื่อส่งแจ้งเตือน Telegram
    if dust_val > PM25_ALERT_THRESHOLD:
        print("⚠️ ค่าฝุ่น PM2.5 เกินเกณฑ์ความปลอดภัย ({:.2f} > {})!".format(dust_val, PM25_ALERT_THRESHOLD))
        send_telegram_alert(dust_val, gas_ppm, current_time, device_id="a1")

    # บันทึกข้อมูลลง NocoDB
    data = {
        "Device ID": "a1",
        "PM 2.5 Value": dust_val,
        "Gas Type": "co",
        "Gas Value": gas_ppm,
        "Timestamp": current_time
    }

    try:
        print("Sending data to NocoDB...")
        noco_bytes = ujson.dumps(data).encode('utf-8')
        noco_headers = {
            "accept": "application/json",
            "xc-token": "U3WjT_etA7hXLe2uFhVhFYvLppouR3-W--CqCnO8",
            "Content-Type": "application/json",
            "Content-Length": str(len(noco_bytes))
        }
        response = urequests.post(url, headers=noco_headers, data=noco_bytes)
        print("Status Code:", response.status_code)
        print("Response text:", response.text)
        response.close()
    except Exception as e:
        print("Error sending data:", e)

    print("-----------------------------------")
    time.sleep(10)
