# 🌿 AirGuard - ระบบติดตามคุณภาพอากาศ PM 2.5 & ก๊าซ Real-time

เว็บแอปพลิเคชันสำหรับเฝ้าระวังคุณภาพอากาศและฝุ่นละออง PM 2.5 แบบ Real-time ที่ออกแบบมาเพื่อเผยแพร่บน **GitHub Pages** ได้ทันที โดยดึงข้อมูลโดยตรงจาก **NocoDB API** ผ่านทาง Client-side JavaScript

🔗 **GitHub Repository**: [https://github.com/38920-student/pm2.5-web](https://github.com/38920-student/pm2.5-web)  
🌐 **ลิงก์หน้าเว็บ GitHub Pages (เมื่อเปิดใช้งาน)**: [https://38920-student.github.io/pm2.5-web/](https://38920-student.github.io/pm2.5-web/)

---

## ✨ ฟีเจอร์เด่น (Features)

1. **Dashboard แสดงผลแบบ Real-time**
   - แสดงระดับฝุ่น PM 2.5 และก๊าซ (Gas / CO) ล่าสุด
   - ประเมินสถานะและคำแนะนำสุขภาพตามเกณฑ์มาตรฐานประเทศไทย (PCD Air Quality Standards)
   - แถบสีและไอคอนบอกระดับความปลอดภัย (อากาศดีมาก, อากาศดี, ปานกลาง, เริ่มมีผลกระทบ, มีผลกระทบต่อสุขภาพ)

2. **กราฟแนวโน้มแบบโต้ตอบ (Interactive Chart.js)**
   - กราฟเส้นแสดงความสัมพันธ์ระหว่าง PM 2.5 และระดับก๊าซ
   - สลับดูเฉพาะ PM 2.5, ก๊าซ หรือดูพร้อมกันทั้งสองแกน
   - เลือกแสดงข้อมูล 15, 30, 50 หรือ 100 รายการล่าสุด

3. **ระบบอัปเดตข้อมูลอัตโนมัติ (Auto-refresh)**
   - ตั้งเวลารีเฟรชอัตโนมัติ (5 วิ, 10 วิ, 30 วิ, 1 นาที หรือปิด)
   - ตัวนับเวลาถอยหลัง (Countdown timer)
   - ปุ่มกดรีเฟรชทันที (Manual Refresh)

4. **ตารางประวัติและการส่งออกข้อมูล (History & Export)**
   - ตารางรายการย้อนหลังพร้อมระบบแบ่งหน้า (Pagination)
   - ค้นหาข้อมูลแบบ Real-time ตาม ID, วันเวลา, อุปกรณ์
   - ตัวกรองช่วงวันที่ (Date Filter)
   - ส่งออกข้อมูลเป็นไฟล์ Excel / CSV รองรับภาษาไทย (UTF-8 BOM)

5. **ตั้งค่าการเชื่อมต่อ NocoDB API ได้อย่างอิสระ**
   - มี Modal ให้เปลี่ยน Base URL, Table ID, Token ได้เองผ่านหน้าเว็บ
   - บันทึกการตั้งค่าลง `localStorage` ของเบราว์เซอร์อัตโนมัติ

---

## 🚀 วิธีเผยแพร่และเปิดใช้งานบน GitHub Pages (Step-by-step Guide)

ทำตามขั้นตอนด้านล่างนี้เพื่อเปิดใช้งานเว็บไซต์บน GitHub Pages:

### ขั้นตอนที่ 1: อัปโหลด / Push โค้ดขึ้น GitHub
เมื่อมีการแก้ไขไฟล์ในโฟลเดอร์ ให้ส่งโค้ดขึ้น repository บน GitHub:
```bash
git add .
git commit -m "Add modern Air Quality dashboard for GitHub Pages"
git push origin main
```

---

### ขั้นตอนที่ 2: เปิดใช้งาน GitHub Pages ในการตั้งค่า Repository
1. เข้าไปที่หน้า GitHub Repository ของคุณ: [https://github.com/38920-student/pm2.5-web](https://github.com/38920-student/pm2.5-web)
2. คลิกที่แท็บ **Settings** (เมนูบนขวาของ repo)
3. เมนูด้านซ้าย เลือก **Pages** (ใต้หัวข้อ Code and automation)
4. ในส่วน **Build and deployment**:
   - **Source**: เลือก `Deploy from a branch`
   - **Branch**: เลือก `main` และโฟลเดอร์เป็น `/ (root)`
5. คลิกปุ่ม **Save**

---

### ขั้นตอนที่ 3: เข้าใช้งานหน้าเว็บไซต์
- รอประมาณ 1–2 นาที GitHub จะทำการ Build และ Deploy หน้าเว็บ
- เข้าชมเว็บไซต์ได้ที่ URL:  
  👉 **`https://38920-student.github.io/pm2.5-web/`**

---

## 💻 การทดสอบใช้งานในเครื่อง Local (Optional)

หากต้องการเปิดทดสอบบนเครื่องคอมพิวเตอร์ของคุณ สามารถทำได้ 2 วิธี:

### วิธีที่ 1: ดับเบิลคลิกเปิดไฟล์
- ดับเบิลคลิกไฟล์ `index.html` เพื่อเปิดบน Google Chrome, Microsoft Edge หรือเบราว์เซอร์ใดก็ได้

### วิธีที่ 2: รันผ่าน Python Flask
```bash
pip install -r requirements.txt
python app.py
```
เปิดเบราว์เซอร์ไปที่ `http://localhost:5000`
