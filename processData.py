import pandas as pd
import numpy as np

# 전역 변수 설정
stops_file_path = "only_land_data/stops.txt"
stop_times_path = "only_land_data/over11_stop_time.csv"
trips_path = "raw_data/trips.txt"





"""두 지점 간의 거리를 계산하는 함수"""
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1))*np.cos(np.radians(lat2))* np.sin(dlon/2)**2
    c = 2*np.arcsin(np.sqrt(a))
    return R*c



"""데이터 파일들을 로드하는 함수""" 
def load_data():
    stops = pd.read_csv(stops_file_path)
    stop_times = pd.read_csv(stop_times_path, encoding='utf-8')
    trips = pd.read_csv(trips_path)
    return stops, stop_times, trips



"""사용자 위치에서 가까운 정류장을 찾는 함수"""
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



"""정류장 도착 시간 이후의 도착 예정 버스를 필터링하는 함수"""
def filter_future_arrivals(stop_times, stops, trips, closest_stops, arrival_time):
    filtered_stop_times = stop_times[stop_times['stop_id'].isin(closest_stops['stop_id'])]
    future_departures = filtered_stop_times[filtered_stop_times['arrival_time'] > arrival_time]
    future_departures_with_trips = future_departures.merge(trips, on='trip_id', how='inner')
    return future_departures_with_trips.merge(stops[['stop_id', 'stop_name']], on='stop_id', how='left')



"""도착지 반경 내의 모든 정류장을 찾는 함수"""
def find_arrival_stops(stops, user_arrival_lat, user_arrival_lon, arrival_radius):
    """도착지 반경 내의 모든 정류장을 찾는 함수"""
    stops['arrival_distance_km'] = stops.apply(
        lambda row: haversine(user_arrival_lat, user_arrival_lon, row['stop_lat'], row['stop_lon']), axis=1
    )
    return stops[stops['arrival_distance_km'] <= arrival_radius]



"""6. 출발지와 도착지를 연결하는 버스 노선을 찾는 함수"""
def find_matching_routes(departure_buses, arrival_buses, stops, present_time):
    # departure_buses와 arrival_buses의 route_id 비교
    departure_routes = set(departure_buses['trip_id'])
    arrival_routes = set(arrival_buses['trip_id'])
    common_routes = departure_routes.intersection(arrival_routes)

    if not common_routes:
        print("매칭되는 route_id가 없습니다.")
        return
    
    print("\n매칭되는 버스 노선:")
    # 모든 trip_id와 출발/도착 시간을 저장할 리스트
    trip_times = []
    
    for trip_id in common_routes:
        trip_info = get_valid_trips(trip_id, departure_buses, arrival_buses)
        if trip_info:
            departure_rows, valid_arrivals_rows = trip_info
            # 출발 정류장까지 걸어가는 시간을 고려하여 유효한 출발 정류장 필터링
            if not departure_rows.empty:
                trip_times.append((trip_id, departure_rows, valid_arrivals_rows))
    
    # sorted_trips로 정렬된 값 받아오기 
    sorted_trip_times = sort_trips([(t[0], t[1]) for t in trip_times], stops, present_time)
    # 정렬된 trip_times 생성
    sorted_full_trip_times = []
    for sorted_trip_id, sorted_departure_stop in sorted_trip_times:
        # 원래 trip_times에서 해당 trip_id의 arrival_rows 찾기
        for orig_trip_id, _, arrival_rows in trip_times:
            if orig_trip_id == sorted_trip_id:
                sorted_full_trip_times.append((sorted_trip_id, sorted_departure_stop, arrival_rows))
                break
    
    # 정렬된 trip_times 중 n개만 출력을 위한 작업
    process_trips(sorted_full_trip_times, stops, 5)



            



"""trip_id가 동일한 출발 정류장과 도착 정류장 찾기
   7. 출발 정류장 출발 시간보다 늦게 도착하는 도착 정류장만 필터링"""
def get_valid_trips(trip_id, departure_buses, arrival_buses):

    departure_rows = departure_buses[departure_buses['trip_id'] == trip_id]
    arrival_rows = arrival_buses[arrival_buses['trip_id'] == trip_id]

    departure_departure_time = departure_rows['departure_time'].iloc[0]
    valid_arrivals_rows = arrival_rows[arrival_rows['arrival_time'] > departure_departure_time]

    return (departure_rows, valid_arrivals_rows) if not valid_arrivals_rows.empty else None



"""12. 도보 시간을 고려한 유효한 출발 정류장 찾기"""
def find_matching_departure_stops(departure_rows, present_time):
    # 거리 계산에 사용할 컬럼 선택
    distance_col = 'departure_distance_km' if 'departure_distance_km' in departure_rows.columns else 'distance_km'
    
    # Series를 단일 값으로 변환 (첫 번째 행의 값 사용)
    walking_minutes = float(departure_rows[distance_col].iloc[0] * 15)
    
    # 현재 시간에 도보 시간을 더해서 실제 정류장 도착 시간 계산
    time_to_stop = pd.to_datetime(present_time) + pd.Timedelta(minutes=walking_minutes)
    time_to_stop = time_to_stop.strftime('%H:%M:%S')

    # 버스 도착 시간이 정류장 도착 시간보다 늦은 것만 필터링
    valid_departure_rows = departure_rows[departure_rows['arrival_time'] > time_to_stop]
    return valid_departure_rows


"""8. 출발 정류장 출발 시간 기준 정렬"""
def sort_trips(trip_times, stops, present_time):
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
        valid_departure_stops = find_matching_departure_stops(closest_departure_stop, present_time)
        
        if valid_departure_stops.empty:
            continue

        valid_departure_time = valid_departure_stops['arrival_time'].iloc[0]

        for_sort_trip_times.append((valid_departure_time, trip_id, valid_departure_stops))
    
    # departure_time으로 정렬
    for_sort_trip_times.sort(key=lambda x: x[0])
    
    return [(trip_id, closest_departure_stop) for _, trip_id, closest_departure_stop in for_sort_trip_times]


        




""" 9. 도착지와 도착 정류장 사이의 거리가 가장 가까운 도착 정류장 반환,
    도착 정류장 정보 추가, 10. 정류장까지 걸어가는 시간 계산"""
def process_trips(trip_times, stops, trip_count):
    count = 0
    i = 1
    while count < trip_count and i <= len(trip_times):
        trip_id, departure_rows, arrival_rows = trip_times[i-1]

        
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
        closest_departure_stop.loc[:, 'time_to_stop'] = closest_departure_stop['departure_distance_km'] * 15
        closest_arrival_stop.loc[:, 'time_to_stop'] = closest_arrival_stop['arrival_distance_km'] * 15
        
        

        # "장안등기소" 체크 및 출력 로직
        if not closest_arrival_stop['stop_name'].str.contains('장안등기소').any():
        #if not closest_departure_stop.empty: # 특정 정류장 제외 안 함
            count += 1
            print_bus_info(count, trip_id, closest_departure_stop, closest_arrival_stop)
        i += 1




    
# n 개의 버스 정보 출력
def print_bus_info(count, trip_id, closest_departure_stop, closest_arrival_stop):
            if str(trip_id).startswith('RR'):
                print(f"\n{count}번째로 빠른 지하철:")
                print(f"trip ID: {trip_id}")
                print("\n현위치에서 출발 역까지 걸어가는데 걸리는 시간: ", round(closest_departure_stop['time_to_stop'].iloc[0]), "분")
                print("\n출발 역 정보:")
                print(closest_departure_stop[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                        'arrival_time', 'departure_time', 'stop_sequence',
                                        'departure_distance_km']])
                
                print("\n도착 역 정보:")
                print(closest_arrival_stop[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                        'arrival_time', 'departure_time', 'stop_sequence',
                                        'arrival_distance_km']])
                print("\n도착 역에서 목적지까지 걸어가는데 걸리는 시간: ", round(closest_arrival_stop['time_to_stop'].iloc[0]), "분")


            else:
                print(f"\n{count}번째로 빠른 버스:")
                print(f"trip ID: {trip_id}")

                print("\n현위치에서 출발 정류장까지 걸어가는데 걸리는 시간: ", round(closest_departure_stop['time_to_stop'].iloc[0]), "분")
                print("\n출발 정류장 정보:")
                print(closest_departure_stop[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                        'arrival_time', 'departure_time', 'stop_sequence',
                                        'departure_distance_km']])
                
                print("\n도착 정류장 정보:")
                print(closest_arrival_stop[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                        'arrival_time', 'departure_time', 'stop_sequence',
                                        'arrival_distance_km']])
                print("\n도착 정류장에서 목적지까지 걸어가는데 걸리는 시간: ", round(closest_arrival_stop['time_to_stop'].iloc[0]), "분")
            
            print("\n" + "="*50)


    
        










