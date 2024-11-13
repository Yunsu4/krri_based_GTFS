
def convert_time_to_minutes(time_str):
    # 시:분:초를 분으로 변환
    hours, minutes, seconds = map(int, time_str.split(':'))
    return (hours * 60) + minutes + (seconds / 60)


def sort(processed_trips):
    sorted_trips = []
    
    for trip_id, closest_departure_stop, closest_arrival_stop in processed_trips:
        departure_minutes = convert_time_to_minutes(closest_departure_stop['departure_time'].iloc[0])
        arrival_minutes = convert_time_to_minutes(closest_arrival_stop['arrival_time'].iloc[0])
        
        total_time = arrival_minutes - departure_minutes
        total_time += closest_departure_stop['time_to_stop'].iloc[0]
        total_time += closest_arrival_stop['time_to_stop'].iloc[0]
        total_time = round(total_time)
        
        closest_departure_stop['total_journey_time'] = total_time
        sorted_trips.append((trip_id, closest_departure_stop, closest_arrival_stop))
    
    return sorted(sorted_trips, 
                 key=lambda x: (round(x[1]['total_journey_time'].iloc[0]), 
                              convert_time_to_minutes(x[1]['arrival_time'].iloc[0])))
