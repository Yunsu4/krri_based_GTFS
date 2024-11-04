import processData

present_time = "23:00:00"
user_lat, user_lon = 37.303042, 126.966261 # 율전중
#user_lat, user_lon = 37.312651, 126.952781 # 철도연
user_arrival_lat, user_arrival_lon = 37.295089, 126.976882 # 성대 자과캠
#user_arrival_lat, user_arrival_lon = 37.266224, 126.999893 # 수원역
#user_arrival_lat, user_arrival_lon = 37.554725, 126.970740 # 서울역
user_radius = 1  # 사용자 반경을 킬로미터 단위로 설정
arrival_radius = 2  # 도착지 반경을 킬로미터 단위로 설정

def main():
    stops, stop_times, trips = processData.load_data()


    # 1. A지점 반경 1km내 정류장 중 가까운 거 100개
    departure_stops = processData.find_closest_stops(stops, user_lat, user_lon, user_radius, 100,'departure_distance_km')

    if not departure_stops.empty:
 
        # 3. 정류장 도착 이후 출발하는 버스 매칭
        departure_buses = processData.filter_future_arrivals(stop_times, stops, trips, departure_stops, present_time)
        print(f"정류장 도착 이후 출발하는 버스: {len(departure_buses)}개\n")
        #여기에서 결과로 ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence',
        #'pickup_type', 'drop_off_type', 'route_id', 'service_id', 'stop_name'] 가짐
        # stop_times의 모든 열, trips의 모든 열, stop_name을 가짐


        # 4. 도착지 반경 0.6km내 버스 정류장 100개 탐색
        arrival_stops = processData.find_closest_stops(stops, user_arrival_lat, user_arrival_lon, arrival_radius, 100,'arrival_distance_km')


        # 5. 현재 시간 이후에 도착하는 버스 매칭
        arrival_buses = processData.filter_future_arrivals(stop_times, stops, trips, arrival_stops, present_time)
        print(f"현재 시간 이후 출발로 매칭된 도착지 버스: {len(arrival_buses)}개")



        # 6. 출발지와 도착지를 연결하는 버스 노선 찾기
        processData.find_matching_routes(departure_buses, arrival_buses, stops, present_time)

    else:
        print("반경 1km 내에 정류장이 없습니다.")

if __name__ == "__main__":
    main()
