import network
import urequests
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
# 4. Helper Functions
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

# ==========================================
# 5. Main Loop
# ==========================================
while True:
    dust_val, dust_volt = get_smooth_dust(samples=10)
    gas_status, gas_raw, gas_volt, gas_ppm = read_gas_sensor(samples=10)
    current_time = get_iso_timestamp()

    print("Timestamp:", current_time)
    print("ฝุ่น PM2.5: {} µg/m³ (แรงดัน: {:.2f}V)".format(dust_val, dust_volt))
    print("ก๊าซ MQ-135: Raw = {} | แรงดัน = {:.2f}V | PPM = {:.2f} ppm | สถานะ: {}".format(gas_raw, gas_volt, gas_ppm, gas_status))

    # NocoDB v2 API รับ JSON Object โดยตรง (ไม่ต้องครอบด้วย list และไม่ต้องมี "fields")
    data = {
        "Device ID": "a1",
        "PM 2.5 Value": dust_val,
        "Gas Type": "co",
        "Gas Value": gas_ppm,
        "Timestamp": current_time
    }

    try:
        print("Sending data to NocoDB...")
        response = urequests.post(url, headers=headers, json=data)
        print("Status Code:", response.status_code)
        print("Response text:", response.text)
        response.close()
    except Exception as e:
        print("Error sending data:", e)

    print("-----------------------------------")
    time.sleep(10)
