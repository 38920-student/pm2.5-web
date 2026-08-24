import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ตัวแปรเก็บค่าฝุ่นล่าสุด
latest_data = {
    "pm25": 0,
    "status": "รอข้อมูล..."
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ระบบเฝ้าระวังฝุ่น PM2.5</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f9; padding: 20px; }
        .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        .val { font-size: 48px; font-weight: bold; color: #ff5722; margin: 10px 0; }
        .status { font-size: 20px; color: #555; }
    </style>
</head>
<body>
    <div class="card">
        <h2>ค่าฝุ่น PM2.5 ปัจจุบัน</h2>
        <div class="val" id="pm25">{{ pm25 }} µg/m³</div>
        <div class="status" id="status">{{ status }}</div>
    </div>
    <script>
        setInterval(() => {
            fetch('/data')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('pm25').innerText = data.pm25 + ' µg/m³';
                    document.getElementById('status').innerText = data.status;
                });
        }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, pm25=latest_data['pm25'], status=latest_data['status'])

@app.route('/update', methods=['POST'])
def update():
    global latest_data
    req_data = request.get_json()
    if req_data and 'pm25' in req_data:
        pm_val = float(req_data['pm25'])
        status = "ปกติ"
        if pm_val > 50: status = "เริ่มมีผลกระทบ"
        if pm_val > 90: status = "มีผลกระทบต่อสุขภาพ"
        latest_data = {"pm25": pm_val, "status": status}
        return jsonify({"message": "Success"}), 200
    return jsonify({"message": "Invalid data"}), 400

@app.route('/data')
def get_data():
    return jsonify(latest_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)