from copy import deepcopy

def sort(processed_trips, taxi_first):    

    trips_copy = deepcopy(processed_trips)

    sorted_trips = sorted(trips_copy, 
                 key=lambda x: (
                     x['departure']['time_to_stop'],  
                     convert_time_to_minutes(x['departure']['arrival_time'])
                 )) if taxi_first else sorted(trips_copy, 
                 key=lambda x: (
                     x['arrival']['time_to_stop'],  
                     convert_time_to_minutes(x['departure']['arrival_time'])
                 ))

    return sorted_trips

def convert_time_to_minutes(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    return hours * 60 + minutes + seconds / 60
