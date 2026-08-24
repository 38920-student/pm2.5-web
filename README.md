# 🌿 AirGuard - ระบบติดตามคุณภาพอากาศ PM 2.5 & ก๊าซ Real-time

เว็บแอปพลิเคชันและเฟิร์มแวร์สำหรับเฝ้าระวังคุณภาพอากาศและฝุ่นละออง PM 2.5 แบบ Real-time ที่ออกแบบมาเพื่อเผยแพร่บน **GitHub Pages** ได้ทันที โดยดึงข้อมูลโดยตรงจาก **NocoDB API** (`noco.phukhieo.ac.th`) และรองรับระบบแจ้งเตือนผ่าน **Telegram** อัตโนมัติเมื่อค่าฝุ่นเกินเกณฑ์มาตรฐาน

🔗 **GitHub Repository**: [https://github.com/38920-student/pm2.5-web](https://github.com/38920-student/pm2.5-web)  
🌐 **ลิงก์หน้าเว็บ GitHub Pages**: [https://38920-student.github.io/pm2.5-web/](https://38920-student.github.io/pm2.5-web/)

---

## 📡 ข้อมูลการเชื่อมต่อ NocoDB API (Current Endpoint)

- **API Base URL**: `https://noco.phukhieo.ac.th`
- **Table ID**: `mmo2nkzx4m7mc2d`
- **API Endpoint**: `https://noco.phukhieo.ac.th/api/v2/tables/mmo2nkzx4m7mc2d/records?limit=25&sort=-Id`
- **Header Auth**: `xc-token: U3WjT_etA7hXLe2uFhVhFYvLppouR3-W--CqCnO8`

---

## 📱 ระบบแจ้งเตือนผ่าน Telegram (เมื่อ PM 2.5 > 75 µg/m³)

เมื่อเซนเซอร์ตรวจวัดพบค่าฝุ่น PM 2.5 เกิน **75.0 µg/m³** (ระดับมีผลกระทบต่อสุขภาพ) ระบบจะส่งข้อความแจ้งเตือนภาษาไทยเข้าสู่ Telegram ทันที:

### ตัวอย่างข้อความแจ้งเตือน:
```
🚨 แจ้งเตือนคุณภาพอากาศวิกฤต! 🚨

⚠️ ค่าฝุ่น PM 2.5 เกินมาตรฐานความปลอดภัย
━━━━━━━━━━━━━━━━━━━━
🔴 สถานะ: มีผลกระทบต่อสุขภาพ (Hazardous)
📊 ค่า PM 2.5: 82.40 µg/m³ (เกณฑ์วิกฤต > 75.0)
💨 ระดับก๊าซ: 540.20 PPM
📍 อุปกรณ์: a1
🕒 เวลาตรวจวัด: 2026-08-24 15:10:00+00:00
━━━━━━━━━━━━━━━━━━━━
😷 คำแนะนำด้านสุขภาพ:
• หลีกเลี่ยงกิจกรรมกลางแจ้งทุกประเภท
• ปิดประตูหน้าต่างให้มิดชิด และเปิดเครื่องฟอกอากาศ
• สวมหน้ากากป้องกันฝุ่น N95 ทันทีเมื่อจำเป็นต้องออกนอกอาคาร
```

### วิธีตั้งค่า Telegram Token & Chat ID
1. **ในไฟล์ `main.py` (สำหรับบอร์ด ESP32 / MicroPython):**
   ```python
   TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # เช่น "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
   TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"      # เช่น "123456789" หรือ "-100123456789"
   ```
2. **บนหน้า Dashboard เว็บไซต์:**
   - กดปุ่มรูปไอคอน **ตั้งค่า (Gear)** มุมบนขวา
   - กรอก Telegram Bot Token และ Chat ID
   - กดปุ่ม **ทดสอบส่ง Telegram** เพื่อยืนยันการเชื่อมต่อ
   - กด **บันทึกการตั้งค่า**

---

## ✨ ฟีเจอร์เด่น (Features)

1. **Dashboard แสดงผลแบบ Real-time**
   - แสดงระดับฝุ่น PM 2.5 และก๊าซ (Gas / CO) ล่าสุด
   - ประเมินสถานะและคำแนะนำสุขภาพตามเกณฑ์มาตรฐานประเทศไทย (PCD Air Quality Standards)
   - แถบสีและไอคอนบอกระดับความปลอดภัย

2. **กราฟแนวโน้มแบบโต้ตอบ (Interactive Chart.js)**
   - กราฟเส้นแสดงความสัมพันธ์ระหว่าง PM 2.5 และระดับก๊าซ
   - สลับดูเฉพาะ PM 2.5, ก๊าซ หรือดูพร้อมกันทั้งสองแกน

3. **ระบบอัปเดตข้อมูลอัตโนมัติ (Auto-refresh)**
   - ตั้งเวลารีเฟรชอัตโนมัติ (5 วิ, 10 วิ, 30 วิ, 1 นาที หรือปิด)
   - ตัวนับเวลาถอยหลัง (Countdown timer)

4. **ตารางประวัติและการส่งออกข้อมูล (History & Export)**
   - ตารางรายการย้อนหลังพร้อมระบบแบ่งหน้า (Pagination)
   - ค้นหาข้อมูลแบบ Real-time และตัวกรองช่วงวันที่
   - ส่งออกข้อมูลเป็นไฟล์ Excel / CSV รองรับภาษาไทย (UTF-8 BOM)

---

## 🚀 วิธีเผยแพร่และเปิดใช้งานบน GitHub Pages

```bash
git add .
git commit -m "Add Telegram alert feature for PM2.5 > 75"
git push origin main
```
