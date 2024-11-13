import processData

# 출력 로직
def print_trip_info(processed_trips, sort_type, print_count, journey_stops_by_trip):
    count = 1  # 출력한 개수를 세는 카운터
    
    for trip_id, closest_departure_stop, closest_arrival_stop in processed_trips:
        if count > print_count:  # print_count 초과 출력하지 않음
            break
            
        if sort_type == "total_journey_time":
            print_bus_info_total_journey_time(count, trip_id, closest_departure_stop, closest_arrival_stop, journey_stops_by_trip)
        elif sort_type == "taxi_distance":
            print_bus_info(count, trip_id, closest_departure_stop, closest_arrival_stop, journey_stops_by_trip)
        elif sort_type == "walking_distance":
            print_bus_info(count, trip_id, closest_departure_stop, closest_arrival_stop, journey_stops_by_trip)
        else:
            print_bus_info(count, trip_id, closest_departure_stop, closest_arrival_stop, journey_stops_by_trip)
        count += 1

def print_course_of_journey(journey_stops_by_trip, current_trip_id):
    if current_trip_id in journey_stops_by_trip:  # 현재 trip_id가 딕셔너리에 있는지 확인
        journey_stops = journey_stops_by_trip[current_trip_id]
        sorted_stops = sorted(journey_stops, 
                            key=lambda x: x['stop_sequence'].iloc[0])
        
        for stop in sorted_stops:
            print(stop)
        print("\n" + "="*50)

# n 개의 버스 정보 출력
def print_bus_info(count, trip_id, closest_departure_stop, closest_arrival_stop, journey_stops_by_trip):
    if str(trip_id).startswith('RR'):
        print(f"\n{count}번째로 빠른 지하철:")
        print(f"trip ID: {trip_id}")
        print("\n현위치에서 출발 역까지 걸어가는데 걸리는 시간: ", round(closest_departure_stop['time_to_stop'].iloc[0]), "분")
        print("\n출발 역 정보:")
        print(closest_departure_stop[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                'arrival_time', 'departure_time', 'stop_sequence',
                                'departure_distance_km']])
        
        print("\n" + "="*10)
        print("\n출발 역에서 도착 역까지 경유하는 정류장 정보:")
        print_course_of_journey(journey_stops_by_trip, trip_id)    




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
        
        print("\n" + "="*50)
        print("\n출발 역에서 도착 역까지 경유하는 정류장 정보:")
        print_course_of_journey(journey_stops_by_trip, trip_id)

        print("\n도착 정류장 정보:")
        print(closest_arrival_stop[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                'arrival_time', 'departure_time', 'stop_sequence',
                                'arrival_distance_km']])
        print("\n도착 정류장에서 목적지까지 걸어가는데 걸리는 시간: ", round(closest_arrival_stop['time_to_stop'].iloc[0]), "분")
    
    print("\n" + "="*100)




def print_bus_info_total_journey_time(count, trip_id, closest_departure_stop, closest_arrival_stop, journey_stops_by_trip):
    if str(trip_id).startswith('RR'):
        print(f"\n{count}번째로 빠른 지하철:")
        print(f"trip ID: {trip_id}")
        print("\n총 소요 시간: ", round(closest_departure_stop['total_journey_time'].iloc[0]), "분")
        print("\n현위치에서 출발 역까지 걸어가는데 걸리는 시간: ", round(closest_departure_stop['time_to_stop'].iloc[0]), "분")
        print("\n출발 역 정보:")
        print(closest_departure_stop[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                'arrival_time', 'departure_time', 'stop_sequence',
                                'departure_distance_km']])
        
        print("\n" + "="*50)
        print("\n출발 역에서 도착 역까지 경유하는 정류장 정보:")
        print_course_of_journey(journey_stops_by_trip, trip_id)

        print("\n도착 역 정보:")
        print(closest_arrival_stop[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                'arrival_time', 'departure_time', 'stop_sequence',
                                'arrival_distance_km']])
        print("\n도착 역에서 목적지까지 걸어가는데 걸리는 시간: ", round(closest_arrival_stop['time_to_stop'].iloc[0]), "분")


    else:
        print(f"\n{count}번째로 빠른 버스:")
        print(f"trip ID: {trip_id}")
        print("\n총 소요 시간: ", round(closest_departure_stop['total_journey_time'].iloc[0]), "분")
        print("\n현위치에서 출발 정류장까지 걸어가는데 걸리는 시간: ", round(closest_departure_stop['time_to_stop'].iloc[0]), "분")
        print("\n출발 정류장 정보:")
        print(closest_departure_stop[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                'arrival_time', 'departure_time', 'stop_sequence',
                                'departure_distance_km']])
        
        print("\n" + "="*50)
        print("\n출발 역에서 도착 역까지 경유하는 정류장 정보:")
        print_course_of_journey(journey_stops_by_trip, trip_id)

        print("\n도착 정류장 정보:")
        print(closest_arrival_stop[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 
                                'arrival_time', 'departure_time', 'stop_sequence',
                                'arrival_distance_km']])
        print("\n도착 정류장에서 목적지까지 걸어가는데 걸리는 시간: ", round(closest_arrival_stop['time_to_stop'].iloc[0]), "분")
    
    print("\n" + "="*100)


