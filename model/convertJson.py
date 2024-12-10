import json
import model.processData as processData
from util.utilFunctions import custom_round


def convert_trip_info_to_json(processed_trips, print_count, journey_stops_by_trip, routes, taxi_first):
    result = []
    count = 1
        
    for processed_trip in processed_trips:
        if count > print_count:
            break
            
        trip_id = processed_trip['trip_id']
        closest_departure_stop = processed_trip['departure']
        closest_arrival_stop = processed_trip['arrival']
            
        trip_info = {
            "rank": count,
            "trip_id": trip_id,
            "transport_type": "버스" if str(trip_id).startswith('BR') else "지하철",
            "route_name": processData.get_route_name(trip_id, routes),
            "taxi_first": "taxi_first" if taxi_first else "walking_first",
            
            "total_journey_time": processed_trip['total_journey_time'],
            
            "departure": {
                "time_to_stop": custom_round(float(closest_departure_stop.get('time_to_stop', 0))),
                "stop_info": {
                    "stop_id": closest_departure_stop.get('stop_id'),
                    "stop_name": closest_departure_stop.get('stop_name'),
                    "stop_lat": float(closest_departure_stop.get('stop_lat', 0)),
                    "stop_lon": float(closest_departure_stop.get('stop_lon', 0)),
                    "arrival_time": closest_departure_stop.get('arrival_time'),
                    "departure_time": closest_departure_stop.get('departure_time'),
                    "stop_sequence": int(closest_departure_stop.get('stop_sequence', 0)),
                    "distance_km": float(closest_departure_stop.get('departure_distance_km', 0))
                }
            },
            
            "arrival": {
                "time_to_stop": custom_round(float(closest_arrival_stop.get('time_to_stop', 0))),
                "stop_info": {
                    "stop_id": closest_arrival_stop.get('stop_id'),
                    "stop_name": closest_arrival_stop.get('stop_name'),
                    "stop_lat": float(closest_arrival_stop.get('stop_lat', 0)),
                    "stop_lon": float(closest_arrival_stop.get('stop_lon', 0)),
                    "arrival_time": closest_arrival_stop.get('arrival_time'),
                    "departure_time": closest_arrival_stop.get('departure_time'),
                    "stop_sequence": int(closest_arrival_stop.get('stop_sequence', 0)),
                    "distance_km": float(closest_arrival_stop.get('arrival_distance_km', 0))
                }
            }
        }
        
        if trip_id in journey_stops_by_trip:
            journey_stops = journey_stops_by_trip[trip_id]
            trip_info["intermediate_stops"] = journey_stops
        
        result.append(trip_info)
        count += 1
    
    return result



