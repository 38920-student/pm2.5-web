from flask import Flask, render_template, request
import requests
from datetime import datetime
import json

app = Flask(__name__)

NOCODB_URL = "https://app.nocodb.com/api/v3/data/p45cglp3uf0pt7z/m3tvvlkrs3gobi6/records"
HEADERS = {
    "xc-token": "nc_pat_hmNMnwKOLq6MI1FcrZ63uyjtPVwCHobqD2K44iFi"
}

def get_air_status(pm_val):
    try:
        pm = float(pm_val)
        if pm <= 15:
            return {'text': 'อากาศดีมาก', 'color': '#10b981', 'bg': 'rgba(16, 185, 129, 0.15)'}
        elif pm <= 37.5:
            return {'text': 'ปานกลาง', 'color': '#f59e0b', 'bg': 'rgba(245, 158, 11, 0.15)'}
        elif pm <= 75:
            return {'text': 'เริ่มมีผลต่อสุขภาพ', 'color': '#f97316', 'bg': 'rgba(249, 115, 22, 0.15)'}
        else:
            return {'text': 'มีผลต่อสุขภาพ (อันตราย)', 'color': '#ef4444', 'bg': 'rgba(239, 68, 68, 0.15)'}
    except:
        return {'text': 'ไม่ทราบสถานะ', 'color': '#94a3b8', 'bg': 'rgba(148, 163, 184, 0.15)'}

@app.route('/')
def index():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    records = []

    try:
        sort_param = json.dumps([{'field': 'Timestamp', 'direction': 'desc'}])
        response = requests.get(NOCODB_URL, headers=HEADERS, params={"limit": 1000, "sort": sort_param})
        data = response.json()
        raw_records = data.get('records', [])
        
        records = [record.get('fields', {}) for record in raw_records if 'fields' in record]
        
        if start_date or end_date:
            filtered = []
            for rec in records:
                ts_str = rec.get('Timestamp')
                if ts_str:
                    try:
                        rec_date = datetime.fromisoformat(ts_str.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                        keep = True
                        if start_date and rec_date < start_date:
                            keep = False
                        if end_date and rec_date > end_date:
                            keep = False
                        if keep:
                            filtered.append(rec)
                    except ValueError:
                        continue
            records = filtered

    except Exception as e:
        print("Error fetching data:", e)
        records = []
        
    latest_data = records[0] if records else {}
    air_status = get_air_status(latest_data.get('PM 2.5 Value', 0))

    chart_labels = [r.get('Timestamp', '')[:16].replace('T', ' ') for r in reversed(records[:15])]
    chart_pm = [r.get('PM 2.5 Value', 0) for r in reversed(records[:15])]
    chart_gas = [r.get('Gas Value', 0) for r in reversed(records[:15])]

    return render_template('index.html', 
                           records=records, 
                           latest=latest_data, 
                           air_status=air_status,
                           start_date=start_date, 
                           end_date=end_date,
                           chart_labels=chart_labels,
                           chart_pm=chart_pm,
                           chart_gas=chart_gas)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
