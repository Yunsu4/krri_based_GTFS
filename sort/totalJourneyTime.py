def convert_time_to_minutes(time_str):
    # 시:분:초를 분으로 변환
    hours, minutes, seconds = map(int, time_str.split(':'))
    return (hours * 60) + minutes + (seconds / 60)


def sort(processed_trips, taxi_first):
    sorted_trips = add_total_journey_time(processed_trips, taxi_first)
    return sorted(sorted_trips, 
                 key=lambda x: (x['total_journey_time'], 
                              convert_time_to_minutes(x['arrival']['arrival_time'])))


def add_total_journey_time(processed_trips, taxi_first):
    sorted_trips = []
    
    for trip in processed_trips:
        departure_minutes = convert_time_to_minutes(trip['departure']['departure_time'])
        arrival_minutes = convert_time_to_minutes(trip['arrival']['arrival_time'])

        
        total_time = arrival_minutes - departure_minutes
        if taxi_first:
            total_time += round(float(trip['departure']['departure_distance_km']))
            total_time += round(float(trip['arrival']['arrival_distance_km']) * 15)
        else:
            total_time += round(float(trip['departure']['departure_distance_km']) * 15)
            total_time += round(float(trip['arrival']['arrival_distance_km']))
            
        trip['total_journey_time'] = round(total_time)
        sorted_trips.append(trip)
    
    return sorted_trips
