from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
import json
import controller.tripsController
from datetime import datetime
import redis
import gzip
from flask import g
from math import isclose


app = Flask(__name__)

# 세션 설정
app.secret_key = 'your_secret_key'

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
Session(app)




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/trips', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        sort_type = data.get('sort_type', 'default')  # 기본 정렬 기준 설정
        print("받은 데이터:", data)

        # 현재 시간 파싱
        datetime_str = data.get('present_time')
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))  # ISO 형식 처리
        present_time = dt.strftime("%H:%M:%S")

        # 새로운 검색 조건 가져오기
        new_conditions = {
            "departure_lat": float(data.get('departure_lat')),
            "departure_lon": float(data.get('departure_lon')),
            "arrival_lat": float(data.get('arrival_lat')),
            "arrival_lon": float(data.get('arrival_lon')),
            "user_radius": int(data.get('user_radius')),
            "arrival_radius": int(data.get('arrival_radius')),
            "present_time": present_time
        }

        # 이전 검색 조건과 비교
        if (
            'processed_trips' in session
            and session.get('processed_trips')
            and are_conditions_equal(session.get('search_conditions', {}), new_conditions)
        ):

            print("기존 데이터로 정렬 중...")

            # 세션에서 데이터 복구
            processed_trips = decompress_data(session['processed_trips'])

            # 데이터 로드 및 정렬 수행
            if not hasattr(g, 'stop_times') or not hasattr(g, 'stops') or not hasattr(g, 'routes'):
                result_for_sort = controller.tripsController.load_data_for_sort(present_time)
                g.stop_times = result_for_sort['stop_times']
                g.stops = result_for_sort['stops']
                g.routes = result_for_sort['routes']

            stop_times = g.stop_times
            stops = g.stops
            routes = g.routes

            result = controller.tripsController.sort_type_by_user_input(
                processed_trips,
                sort_type,
                stop_times,
                stops,
                routes,
                data.get('taxi_first')
            )

            trips_list = result.get('result', [])


            response_data = {
                "trips": trips_list,
                "user_coordinates": session['user_coordinates']
            }

        else:
            print("새로운 검색 수행...")
            session.clear()  # 세션 초기화

            # 새로운 검색 수행
            departure_lat = new_conditions["departure_lat"]
            departure_lon = new_conditions["departure_lon"]
            arrival_lat = new_conditions["arrival_lat"]
            arrival_lon = new_conditions["arrival_lon"]
            user_radius = new_conditions["user_radius"]
            arrival_radius = new_conditions["arrival_radius"]
            taxi_first = data.get('taxi_first')

            result_for_session = controller.tripsController.process_trips(
                departure_lat, departure_lon,
                arrival_lat, arrival_lon,
                present_time, user_radius,
                arrival_radius, taxi_first
            )

            result_for_sort = controller.tripsController.load_data_for_sort(present_time)
            g.stop_times = result_for_sort['stop_times']
            g.stops = result_for_sort['stops']
            g.routes = result_for_sort['routes']

            # 세션에 새로운 검색 조건과 결과 저장
            session['processed_trips'] = compress_data(result_for_session['processed_trips'])
            session['user_coordinates'] = {
                "departure_lat": departure_lat,
                "departure_lon": departure_lon,
                "arrival_lat": arrival_lat,
                "arrival_lon": arrival_lon
            }
            session['search_conditions'] = new_conditions

            # 기본 정렬 수행
            result = controller.tripsController.sort_type_by_user_input(
                decompress_data(session['processed_trips']),
                'default',  # 기본 정렬 기준
                g.stop_times,
                g.stops,
                g.routes,
                taxi_first
            )

            trips_list = result.get('result', [])

            response_data = {
                #"trips": result,
                "trips": trips_list,
                "user_coordinates": session['user_coordinates']
            }


        return jsonify(response_data)

    return render_template('index.html')





# 데이터 압축
def compress_data(data):
    return gzip.compress(json.dumps(data).encode())

# 데이터 복구
def decompress_data(data):
    return json.loads(gzip.decompress(data).decode())


def are_conditions_equal(cond1, cond2):
    return (
        isclose(cond1['departure_lat'], cond2['departure_lat'], abs_tol=1e-5) and
        isclose(cond1['departure_lon'], cond2['departure_lon'], abs_tol=1e-5) and
        isclose(cond1['arrival_lat'], cond2['arrival_lat'], abs_tol=1e-5) and
        isclose(cond1['arrival_lon'], cond2['arrival_lon'], abs_tol=1e-5) and
        cond1['user_radius'] == cond2['user_radius'] and
        cond1['arrival_radius'] == cond2['arrival_radius'] and
        cond1['present_time'] == cond2['present_time']
    )




if __name__ == '__main__':
    app.run(debug=True, port=5000)
