import processData
import sort.taxiDistance
import sort.walkingDistance
import sort.totalJourneyTime
import model.convertJson
import model.loadData


def sort_type_by_user_input(processed_trips, sort_type, stop_times, stops, routes, taxi_first):
    # 정렬 함수 딕셔너리
    sort_functions = {
        'default': lambda x, taxi_first: x,  # taxi_first 파라미터 추가
        'total_journey_time': sort.totalJourneyTime.sort,
        'taxi_distance': sort.taxiDistance.sort,
        'walking_distance': sort.walkingDistance.sort
    }

    # 정렬 수행
    sorted_trips = sort_functions[sort_type](processed_trips, taxi_first)
    
    # 총 소요 시간 정렬이 아닐 경우에만 총 소요 시간 추가
    if not sort_functions[sort_type] == sort.totalJourneyTime.sort:
        add_total_journey_time = sort.totalJourneyTime.add_total_journey_time(sorted_trips, taxi_first)
        sorted_trips = add_total_journey_time

    # 중복 제거
    final_sorted_trips = processData.remove_duplicate_trips(sorted_trips)
    
    # 경로 정보 추가
    journey_stops_by_trip = processData.get_course_of_journey(final_sorted_trips, stop_times, stops)
    
    # JSON 변환
    return model.convertJson.convert_trip_info_to_json(final_sorted_trips, 5, journey_stops_by_trip, routes, taxi_first)






def process_trips(user_lat, user_lon, arrival_lat, arrival_lon, present_time, user_radius, arrival_radius, sort_type, taxi_first):
    stops, routes = model.loadData.load_data()
    stop_times = model.loadData.load_stop_times(present_time)


    # 1. A지점 반경 1km내 정류장 중 가까운 거 100개
    departure_stops = processData.find_closest_stops(stops, user_lat, user_lon, user_radius, 100,'departure_distance_km')

    if not departure_stops.empty:
 
        # 2. 현재 시간 이후 도착하는 버스 매칭
        departure_buses = processData.filter_future_arrivals(stop_times, stops, departure_stops, present_time)
        
        # 3. 도착지 반경 2km내 버스 정류장 100개 탐색
        arrival_stops = processData.find_closest_stops(stops, arrival_lat, arrival_lon, arrival_radius, 100,'arrival_distance_km')

        # 4. 현재 시간 이후에 도착하는 버스 매칭
        arrival_buses = processData.filter_future_arrivals(stop_times, stops, arrival_stops, present_time)

        # 5(6,7,8). 출발지와 도착지를 연결하는 버스 노선 찾기
        sorted_full_trip_times = processData.find_matching_routes(departure_buses, arrival_buses, stops, present_time, taxi_first)
        
        # 9,10.정렬된 trip_times 중 n개만 출력을 위한 작업
        processed_trips = processData.process_trips(sorted_full_trip_times, stops, 10, taxi_first)

        return sort_type_by_user_input(processed_trips, sort_type, stop_times, stops, routes, taxi_first)
