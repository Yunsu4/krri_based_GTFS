import processData
import view.outputView

import sort.taxiDistance
import sort.walkingDistance
import sort.totalJourneyTime

import model.loadData

present_time = "23:00:00"
user_lat, user_lon = 37.303042, 126.966261 # 율전중
#user_lat, user_lon = 37.312651, 126.952781 # 철도연

user_arrival_lat, user_arrival_lon = 37.295089, 126.976882 # 성대 자과캠
#user_arrival_lat, user_arrival_lon = 37.266224, 126.999893 # 수원역
#user_arrival_lat, user_arrival_lon = 37.554725, 126.970740 # 서울역

#user_lat, user_lon = 37.295089, 126.976882 # 성대 자과캠
#user_arrival_lat, user_arrival_lon =  37.303042, 126.966261 # 율전중


user_radius = 1  # 사용자 반경을 킬로미터 단위로 설정
arrival_radius = 2  # 도착지 반경을 킬로미터 단위로 설정




def process_and_print_sorted_trips(processed_trips, sort_type, print_count, stop_times, stops):
    # 정렬 함수 매핑
    sort_functions = {
        "default": lambda x: x,  # 기본 정렬은 이미 되어 있으므로 그대로 반환
        "total_journey_time": sort.totalJourneyTime.sort,
        "taxi_distance": sort.taxiDistance.sort,
        "walking_distance": sort.walkingDistance.sort
    }
    
    # 정렬 타입에 따른 메시지 매핑
    sort_messages = {
        "default": "매칭된 버스 노선 (기본 정렬 - 가장 빨리 탈 수 있는 대중교통)",
        "total_journey_time": "매칭된 버스 노선 (총 소요 시간 정렬)",
        "taxi_distance": "매칭된 버스 노선 (택시 거리 정렬)",
        "walking_distance": "매칭된 버스 노선 (걸어가는 거리 정렬)"
    }
    
    # 정렬 수행
    sorted_trips = sort_functions[sort_type](processed_trips)
    
    # 중복 제거
    final_sorted_trips = processData.remove_duplicate_trips(sorted_trips)
    
    # 경유 정류장 정보 가져오기
    journey_stops = processData.get_course_of_journey(final_sorted_trips, stop_times, stops)
    
    # 결과 출력
    print(sort_messages[sort_type])
    view.outputView.print_trip_info(final_sorted_trips, sort_type, print_count, journey_stops)











def main():

    # 데이터 로드
    stops,trips = model.loadData.load_data()
    stop_times = model.loadData.load_stop_times(present_time)


    # 1. A지점 반경 1km내 정류장 중 가까운 거 100개
    departure_stops = processData.find_closest_stops(stops, user_lat, user_lon, user_radius, 100,'departure_distance_km')

    if not departure_stops.empty:
 
        # 2. 현재 시간 이후 도착하는 버스 매칭
        departure_buses = processData.filter_future_arrivals(stop_times, stops, trips, departure_stops, present_time)
        print(f"정류장 도착 이후 출발하는 버스: {len(departure_buses)}개\n")
        #여기에서 결과로 ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence',
        #'pickup_type', 'drop_off_type', 'route_id', 'service_id', 'stop_name'] 가짐
        # stop_times의 모든 열, trips의 모든 열, stop_name을 가짐


        # 3. 도착지 반경 2km내 버스 정류장 100개 탐색
        arrival_stops = processData.find_closest_stops(stops, user_arrival_lat, user_arrival_lon, arrival_radius, 100,'arrival_distance_km')


        # 4. 현재 시간 이후에 도착하는 버스 매칭
        arrival_buses = processData.filter_future_arrivals(stop_times, stops, trips, arrival_stops, present_time)
        print(f"현재 시간 이후 도착으로 매칭된 도착지 버스: {len(arrival_buses)}개")



        # 5(6,7,8). 출발지와 도착지를 연결하는 버스 노선 찾기
        sorted_full_trip_times = processData.find_matching_routes(departure_buses, arrival_buses, stops, present_time)
        # 9,10.정렬된 trip_times 중 n개만 출력을 위한 작업
        processed_trips = processData.process_trips(sorted_full_trip_times, stops, 10)
        

        

        #process_and_print_sorted_trips(processed_trips, "default", 8, stop_times, stops)
        #process_and_print_sorted_trips(processed_trips, "total_journey_time", 5, stop_times, stops)
        #process_and_print_sorted_trips(processed_trips, "taxi_distance", 5, stop_times, stops)
        #process_and_print_sorted_trips(processed_trips, "walking_distance", 5, stop_times, stops)   
        
        
        # 각 정렬 타입별로 처리 및 출력
        sort_types = {
            "default": 8,  # 기본 정렬은 8개 출력
            "total_journey_time": 5,  # 나머지는 5개씩 출력
            "taxi_distance": 5,
            "walking_distance": 5
        }

        for sort_type, print_count in sort_types.items():
            process_and_print_sorted_trips(processed_trips, sort_type, print_count, stop_times, stops)
            print("\n" + "="*50)

    else:
        print("반경 1km 내에 정류장이 없습니다.")

if __name__ == "__main__":
    main()
 