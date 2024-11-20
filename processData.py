import pandas as pd
import numpy as np

def custom_round(number):
    if isinstance(number, pd.Series):
        number = number.iloc[0]
    
    if number - int(number) >= 0.5:
        return int(number) + 1
    else:
        return int(number)


"""두 지점 간의 거리를 계산하는 함수"""
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1))*np.cos(np.radians(lat2))* np.sin(dlon/2)**2
    c = 2*np.arcsin(np.sqrt(a))
    return R*c




"""1, 3. 사용자 위치에서 가까운 정류장을 찾는 함수"""
def find_closest_stops(stops, user_lat, user_lon, user_radius, stop_count, distance_col='distance_km'):
    stops[distance_col] = stops.apply(
        lambda row: haversine(user_lat, user_lon, row['stop_lat'], row['stop_lon']), axis=1
    )
    
    within_radius = stops[stops[distance_col] <= user_radius]
    
    print(f"반경 내 정류장 수: {len(within_radius)}")
    
    if not within_radius.empty:
        result = within_radius.nsmallest(stop_count, distance_col)
        print(f"반환된 정류장 수: {len(result)}\n")
        return result
    return pd.DataFrame()



"""거리에 따른 도보 시간 계산 함수"""
def calculate_walking_time(distance_km):
    return (distance_km * 15).round(2)



"""2, 4. 현재 시간 이후 도착 예정 버스를 필터링하는 함수"""
def filter_future_arrivals(stop_times, stops, closest_stops, present_time):
    filtered_stop_times = stop_times[stop_times['stop_id'].isin(closest_stops['stop_id'])]
    future_departures = filtered_stop_times[filtered_stop_times['arrival_time'] > present_time]
    return future_departures.merge(stops[['stop_id', 'stop_name']], on='stop_id', how='left')



"""5(6, 7). 출발지와 도착지를 경로로 이어져 있는 버스 노선을 찾는 함수"""
def find_matching_routes(departure_buses, arrival_buses, stops, present_time, taxi_first):
    # departure_buses와 arrival_buses의 route_id 비교
    departure_routes = set(departure_buses['trip_id'])
    arrival_routes = set(arrival_buses['trip_id'])
    common_routes = departure_routes.intersection(arrival_routes)

    if not common_routes:
        print("매칭되는 route_id가 없습니다.")
        return
    
    # 모든 trip_id와 출발/도착 시간을 저장할 리스트
    trip_times = []
    
    # 출발 버스 중 공통된 trip_id를 가지는 버스만 필터링
    for trip_id in common_routes:
        departure_rows = departure_buses[departure_buses['trip_id'] == trip_id]
        if not departure_rows.empty:
            trip_times.append((trip_id, departure_rows))
    
    # 보정 - 출발 정류장의 버스 출발 시간 기준, 노선과 현 시각 매칭
    sorted_trip_times = []
    for trip_id, departure_rows in sort_trips(trip_times, stops, present_time, taxi_first):
        trip_info = get_valid_trips_with_sort(trip_id, departure_rows, arrival_buses)
        if trip_info:
            departure_rows, arrival_rows = trip_info
            sorted_trip_times.append((trip_id, departure_rows, arrival_rows))
    
    return sorted_trip_times



"""6. 출발 정류장 출발 시간 기준 정렬"""
def sort_trips(trip_times, stops, present_time, taxi_first):
    for_sort_trip_times = []
    for trip_id, departure_rows in trip_times:
        departure_stop_ids = departure_rows['stop_id'].values
        departure_stops_info = stops[stops['stop_id'].isin(departure_stop_ids)].copy()
        
        # 먼저 가장 가까운 정류장 찾기
        closest_departure_stop = departure_stops_info.nsmallest(1, 'departure_distance_km')
        
        closest_departure_stop_id = closest_departure_stop['stop_id'].iloc[0]
        closest_departure_times = departure_rows[departure_rows['stop_id'] == closest_departure_stop_id][['departure_time', 'arrival_time', 'stop_sequence']]
        
        closest_departure_stop = closest_departure_stop.assign(
            departure_time=closest_departure_times['departure_time'].iloc[0],
            arrival_time=closest_departure_times['arrival_time'].iloc[0],
            stop_sequence=closest_departure_times['stop_sequence'].iloc[0]
        )
        
        # 도보 시간을 고려한 유효한 출발 정류장 찾기
        valid_departure_stops = find_matching_departure_stops(closest_departure_stop, present_time, taxi_first)
        
        if valid_departure_stops.empty:
            continue

        valid_departure_time = valid_departure_stops['departure_time'].iloc[0]

        for_sort_trip_times.append((valid_departure_time, trip_id, valid_departure_stops))
    
    # departure_time으로 정렬
    for_sort_trip_times.sort(key=lambda x: x[0])
    
    return [(trip_id, closest_departure_stop) for _, trip_id, closest_departure_stop in for_sort_trip_times]


        
"""7. 도보 시간을 고려한 유효한 출발 정류장 찾기"""
def find_matching_departure_stops(departure_rows, present_time, taxi_first):

    # 거리 계산에 사용할 컬럼 선택
    distance_col = 'departure_distance_km' if 'departure_distance_km' in departure_rows.columns else 'distance_km'

    if taxi_first:
        travel_time_to_stop = float(departure_rows[distance_col].iloc[0])    
    else:
        travel_time_to_stop = float(departure_rows[distance_col].iloc[0] * 15)
    
    # 현재 시간에 도보 or 택시 시간을 더해서 실제 정류장 도착 시간 계산
    time_to_stop = pd.to_datetime(present_time) + pd.Timedelta(minutes=travel_time_to_stop)
    time_to_stop = time_to_stop.strftime('%H:%M:%S')

    # 버스 도착 시간이 정류장 도착 시간보다 늦은 것만 필터링
    valid_departure_rows = departure_rows[departure_rows['arrival_time'] > time_to_stop]
    return valid_departure_rows



'''8. 출발 정류장의 버스 출발 시간 보다 늦게 도착하는 도착 정류장 버스만 필터링'''
def get_valid_trips_with_sort(trip_id, departure_rows, arrival_buses):
    arrival_rows = arrival_buses[arrival_buses['trip_id'] == trip_id]

    departure_departure_time = departure_rows['departure_time'].iloc[0]
    valid_arrivals_rows = arrival_rows[arrival_rows['arrival_time'] > departure_departure_time]

    return (departure_rows, valid_arrivals_rows) if not valid_arrivals_rows.empty else None



""" 8. 도착지와 도착 정류장 사이의 거리가 가장 가까운 도착 정류장 반환,
    도착 정류장 정보 추가, 9. 정류장까지 걸어가는 시간 계산"""
def process_trips(trip_times, stops, trip_count, taxi_first):
    processed_trips = []
    
    for trip_id, departure_rows, arrival_rows in trip_times[:trip_count]:  # 정렬된 순서 그대로 사용
        # 도착지 정류장 정보 - 도착지와 가장 가까운 정류장 선택
        arrival_stop_ids = arrival_rows['stop_id'].values
        arrival_stops_info = stops[stops['stop_id'].isin(arrival_stop_ids)].copy()

        closest_arrival_stop = arrival_stops_info.nsmallest(1, 'arrival_distance_km')

        # 가장 가까운 도착 정류장의 버스 시간 정보 가져오기
        closest_arrival_stop_id = closest_arrival_stop['stop_id'].iloc[0]
        closest_arrival_times = arrival_rows[arrival_rows['stop_id'] == closest_arrival_stop_id][['departure_time', 'arrival_time','stop_sequence']]

        # 정류장 정보에 시간 정보 추가
        closest_departure_stop = departure_rows
        
        closest_arrival_stop = closest_arrival_stop.assign(
            departure_time=closest_arrival_times['departure_time'].iloc[0],
            arrival_time=closest_arrival_times['arrival_time'].iloc[0],
            stop_sequence=closest_arrival_times['stop_sequence'].iloc[0]
        )

        # 거리에 따른 도보 시간 계산    
        closest_departure_stop, closest_arrival_stop = calculate_time_to_stop(closest_departure_stop, closest_arrival_stop, taxi_first)
        
        processed_trips.append((trip_id, closest_departure_stop, closest_arrival_stop))
        
    return processed_trips


def calculate_time_to_stop(closest_departure_stop, closest_arrival_stop, taxi_first):
    if taxi_first:
        closest_departure_stop.loc[:, 'time_to_stop'] = custom_round_for_taxi(closest_departure_stop['departure_distance_km'])
        closest_arrival_stop.loc[:, 'time_to_stop'] = custom_round(closest_arrival_stop['arrival_distance_km'] * 15)
    else:
        closest_departure_stop.loc[:, 'time_to_stop'] = custom_round(closest_departure_stop['departure_distance_km'] * 15)
        closest_arrival_stop.loc[:, 'time_to_stop'] = custom_round_for_taxi(closest_arrival_stop['arrival_distance_km'])

    return (closest_departure_stop, closest_arrival_stop)

def custom_round_for_taxi(number):
    if isinstance(number, pd.Series):
        number = number.iloc[0]
    
    if number - int(number) >= 0.4:
        return int(number) + 1
    else:
        return int(number)



''' 11. 동일한 경로의 대중교통이 중복 표시되지 않도록 필터링'''
def remove_duplicate_trips(processed_trips):
    unique_trips = []
    seen_routes = set()
    
    for current_trip in processed_trips:  # 정렬된 순서 그대로 순회
        trip_id = current_trip[0]
        departure = current_trip[1]
        arrival = current_trip[2]
        
        # 출발지-도착지 쌍을 키로 사용
        route_key = (
            departure['stop_id'].iloc[0],
            arrival['stop_id'].iloc[0]
        )
        
        if route_key not in seen_routes:
            seen_routes.add(route_key)
            unique_trips.append(current_trip)
            
    return unique_trips  # 정렬된 순서 유지



def convert_time_to_minutes(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    return hours * 60 + minutes + seconds / 60



''' 12. 노선 경로 출력'''
def get_course_of_journey(processed_trips, stop_times, stops):
    journey_stops_by_trip = {}  # trip_id를 키로 사용하는 딕셔너리

    for trip_id, closest_departure_stop, closest_arrival_stop in processed_trips:
        departure_stop_sequence = closest_departure_stop['stop_sequence'].iloc[0]
        arrival_stop_sequence = closest_arrival_stop['stop_sequence'].iloc[0]
        
        journey_stops = []  # 현재 trip의 경유 정류장들을 저장할 리스트
        
        for i in range(departure_stop_sequence+1, arrival_stop_sequence):
            journey_stop = stop_times[(stop_times['stop_sequence'] == i) & 
                                    (stop_times['trip_id'] == trip_id)]
            if not journey_stop.empty:  # 빈 DataFrame 체크
                stop_id_of_journey = journey_stop['stop_id'].iloc[0]
                stop_id = stops[stops['stop_id'] == stop_id_of_journey]
                journey_stop = journey_stop.merge(stop_id, on='stop_id', how='left')
                journey_stop = journey_stop[['trip_id', 'stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                    'arrival_time', 'departure_time', 'stop_sequence']]
                journey_stops.append(journey_stop)
        
        if journey_stops:  # 경유 정류장이 있는 경우만 저장
            journey_stops_by_trip[trip_id] = journey_stops

    return journey_stops_by_trip



''' 13. 노선 이름 조회'''
def get_trip_name(trip_id, routes):
    try:
        # '_Ord' 이전까지의 문자열을 route_id로 사용
        route_id = trip_id.split('_Ord')[0]  # BR_3100_200000049
        
        matching_routes = routes[routes['route_id'] == route_id]
        
        if matching_routes.empty:
            return f"알 수 없는 노선 (ID: {route_id})"
            
        return matching_routes['route_short_name'].iloc[0]
        
    except Exception as e:
        return f"노선 정보 조회 실패 (Trip ID: {trip_id})"

