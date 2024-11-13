from copy import deepcopy

def sort(processed_trips):

    trips_copy = deepcopy(processed_trips)

    return sorted(trips_copy,
                  key=lambda x: (x[1]['time_to_stop'].iloc[0], 
                                  convert_time_to_minutes(x[1]['arrival_time'].iloc[0])))
    


def convert_time_to_minutes(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    return hours * 60 + minutes + seconds / 60


