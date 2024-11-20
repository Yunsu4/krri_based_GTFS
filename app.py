from flask import Flask, request, jsonify, render_template
import json
import controller.tripsController
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/trips', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        
        print("받은 데이터:", data)  # 디버깅용
        
        departure_lat = float(data.get('departure_lat'))
        departure_lon = float(data.get('departure_lon'))
        arrival_lat = float(data.get('arrival_lat'))
        arrival_lon = float(data.get('arrival_lon'))
        
        # datetime-local 값을 HH:MM:SS 형식으로 변환
        datetime_str = data.get('present_time')
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))  # ISO 형식 처리
        present_time = dt.strftime("%H:%M:%S")

        user_radius = int(data.get('user_radius'))
        arrival_radius = int(data.get('arrival_radius'))
        sort_type = data.get('sort_type')
        taxi_first = data.get('taxi_first')

        result = controller.tripsController.process_trips(
            departure_lat, departure_lon, 
            arrival_lat, arrival_lon, 
            present_time, user_radius, 
            arrival_radius, sort_type, taxi_first
        )
        
        # JSON 응답 반환
        return jsonify(json.loads(result))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
