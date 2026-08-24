import os
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- ตั้งค่า NOCODB ---
NOCODB_URL = "https://app.nocodb.com/wf0x3zfl/p45cglp3uf0pt7z/m3tvvlkrs3gobi6/vwy052qpo06lg1hg/sensor-readings-sensor-readings"  # ใส่ URL Table ของคุณ
NOCODB_TOKEN = "nc_pat_hmNMnwKOLq6MI1FcrZ63uyjtPVwCHobqD2K44iFi"                                   # ใส่ API Token ของ NocoDB

headers = {
    "xc-token": NOCODB_TOKEN,
    "Content-Type": "application/json"
}

def get_nocodb_data():
    """ดึงข้อมูลประวัติจาก NocoDB"""
    try:
        response = requests.get(f"{NOCODB_URL}?limit=15&sort=-Id", headers=headers, timeout=5)
        if response.status_code == 200:
            records = response.json().get('list', [])
            history = []
            for r in records:
                history.append({
                    "time": r.get('created_at', r.get('CreatedAt', '')),
                    "pm25": r.get('pm25', 0),
                    "gas": r.get('gas', 0)
                })
            return history
    except Exception as e:
        print(f"NocoDB Error: {e}")
    return []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ระบบติดตามคุณภาพอากาศ</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .card { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .status-box { border-left: 5px solid #2ecc71; padding-left: 15px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .val-num { font-size: 36px; font-weight: bold; margin-top: 10px; }
        .sub-text { color: #888; font-size: 14px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #eee; }
        th { color: #666; font-weight: 600; }
        .filter-box { display: flex; gap: 10px; align-items: center; margin-bottom: 15px; }
        input[type="date"] { padding: 8px; border: 1px solid #ccc; border-radius: 6px; }
        .btn-search { background: #1a252f; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>ระบบติดตามคุณภาพอากาศ</h2>
            <div class="sub-text" id="time-stamp">--/--/---- --:--:--</div>
        </div>

        <div class="card status-box">
            <div class="sub-text">สถานะอากาศปัจจุบัน</div>
            <h3 style="color: #2ecc71; margin: 5px 0;" id="status-text">กำลังโหลด...</h3>
            <div class="sub-text" style="float: right; margin-top: -25px;">อ้างอิงจาก PM 2.5</div>
        </div>

        <div class="grid-2">
            <div class="card">
                <div class="sub-text">ฝุ่น PM 2.5</div>
                <div class="val-num"><span id="pm25-val">0.00</span> <span style="font-size: 16px; color: #666;">µg/m³</span></div>
            </div>
            <div class="card">
                <div class="sub-text">ระดับก๊าซ (Gas)</div>
                <div class="val-num"><span id="gas-val">0.00</span> <span style="font-size: 16px; color: #666;">PPM</span></div>
            </div>
        </div>

        <div class="card">
            <h3>แนวโน้มค่าฝุ่นและก๊าซ</h3>
            <canvas id="airChart" height="100"></canvas>
        </div>

        <div class="card">
            <div class="filter-box">
                <span class="sub-text">ตั้งแต่:</span>
                <input type="date">
                <span class="sub-text">ถึง:</span>
                <input type="date">
                <button class="btn-search">ค้นหา</button>
            </div>
            <h3>ประวัติการบันทึก (จาก NocoDB)</h3>
            <table>
                <thead>
                    <tr>
                        <th>เวลา</th>
                        <th>PM 2.5</th>
                        <th>ก๊าซ</th>
                    </tr>
                </thead>
                <tbody id="history-table">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('airChart').getContext('2d');
        const airChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'PM 2.5 (µg/m³)', data: [], borderColor: '#3498db', fill: false },
                    { label: 'Gas (PPM)', data: [], borderColor: '#9b59b6', fill: false }
                ]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } }
        });

        function loadData() {
            fetch('/api/data')
                .then(res => res.json())
                .then(data => {
                    if (data.history && data.history.length > 0) {
                        const latest = data.history[0];
                        document.getElementById('pm25-val').innerText = latest.pm25;
                        document.getElementById('gas-val').innerText = latest.gas;
                        document.getElementById('time-stamp').innerText = latest.time;
                        
                        let status = "อากาศดีมาก";
                        if (latest.pm25 > 37.5) status = "เริ่มมีผลกระทบ";
                        if (latest.pm25 > 75.0) status = "มีผลกระทบต่อสุขภาพ";
                        document.getElementById('status-text').innerText = status;

                        // อัปเดตกราฟ
                        const reversedData = [...data.history].reverse();
                        airChart.data.labels = reversedData.map(h => h.time);
                        airChart.data.datasets[0].data = reversedData.map(h => h.pm25);
                        airChart.data.datasets[1].data = reversedData.map(h => h.gas);
                        airChart.update();

                        // อัปเดตตาราง
                        let tableHTML = '';
                        data.history.forEach(h => {
                            tableHTML += `<tr><td>${h.time}</td><td>${h.pm25}</td><td>${h.gas}</td></tr>`;
                        });
                        document.getElementById('history-table').innerHTML = tableHTML;
                    }
                });
        }

        loadData();
        setInterval(loadData, 5000); // อัปเดตข้อมูลทุก 5 วินาที
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def api_data():
    history = get_nocodb_data()
    return jsonify({"history": history})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
