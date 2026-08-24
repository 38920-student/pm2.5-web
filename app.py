import os
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# เก็บประวัติข้อมูลย้อนหลัง
data_history = []

latest_data = {
    "pm25": 0.63,
    "gas": 534.82,
    "status": "อากาศดีมาก",
    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
}

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
            <div class="sub-text" id="time-stamp">{{ timestamp }}</div>
        </div>

        <div class="card status-box">
            <div class="sub-text">สถานะอากาศปัจจุบัน</div>
            <h3 style="color: #2ecc71; margin: 5px 0;" id="status-text">{{ status }}</h3>
            <div class="sub-text" style="float: right; margin-top: -25px;">อ้างอิงจาก PM 2.5</div>
        </div>

        <div class="grid-2">
            <div class="card">
                <div class="sub-text">ฝุ่น PM 2.5</div>
                <div class="val-num"><span id="pm25-val">{{ pm25 }}</span> <span style="font-size: 16px; color: #666;">µg/m³</span></div>
            </div>
            <div class="card">
                <div class="sub-text">ระดับก๊าซ (Gas)</div>
                <div class="val-num"><span id="gas-val">{{ gas }}</span> <span style="font-size: 16px; color: #666;">PPM</span></div>
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
            <h3>ประวัติการบันทึก</h3>
            <table>
                <thead>
                    <tr>
                        <th>เวลา</th>
                        <th>PM 2.5</th>
                        <th>ก๊าซ</th>
                    </tr>
                </thead>
                <tbody id="history-table">
                    {% for row in history %}
                    <tr>
                        <td>{{ row.time }}</td>
                        <td>{{ row.pm25 }}</td>
                        <td>{{ row.gas }}</td>
                    </tr>
                    {% endfor %}
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

        setInterval(() => {
            fetch('/data')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('pm25-val').innerText = data.pm25;
                    document.getElementById('gas-val').innerText = data.gas;
                    document.getElementById('status-text').innerText = data.status;
                    document.getElementById('time-stamp').innerText = data.timestamp;

                    // อัปเดตกราฟ
                    airChart.data.labels = data.history.map(h => h.time.split(' ')[1]);
                    airChart.data.datasets[0].data = data.history.map(h => h.pm25);
                    airChart.data.datasets[1].data = data.history.map(h => h.gas);
                    airChart.update();

                    // อัปเดตตาราง
                    let tableHTML = '';
                    data.history.forEach(h => {
                        tableHTML += `<tr><td>${h.time}</td><td>${h.pm25}</td><td>${h.gas}</td></tr>`;
                    });
                    document.getElementById('history-table').innerHTML = tableHTML;
                });
        }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(
        HTML_TEMPLATE, 
        pm25=latest_data['pm25'], 
        gas=latest_data['gas'], 
        status=latest_data['status'],
        timestamp=latest_data['timestamp'],
        history=data_history
    )

@app.route('/update', methods=['POST'])
def update():
    global latest_data, data_history
    req_data = request.get_json()
    if req_data:
        pm_val = float(req_data.get('pm25', 0))
        gas_val = float(req_data.get('gas', 0))
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        status = "อากาศดีมาก"
        if pm_val > 37.5: status = "เริ่มมีผลกระทบ"
        if pm_val > 75.0: status = "มีผลกระทบต่อสุขภาพ"

        latest_data = {
            "pm25": pm_val,
            "gas": gas_val,
            "status": status,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        # เพิ่มเข้าประวัติ (เก็บสูงสุด 15 ค่าย้อนหลัง)
        data_history.insert(0, {"time": now_str, "pm25": pm_val, "gas": gas_val})
        data_history = data_history[:15]
        
        return jsonify({"message": "Success"}), 200
    return jsonify({"message": "Invalid data"}), 400

@app.route('/data')
def get_data():
    return jsonify({
        "pm25": latest_data['pm25'],
        "gas": latest_data['gas'],
        "status": latest_data['status'],
        "timestamp": latest_data['timestamp'],
        "history": data_history
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
