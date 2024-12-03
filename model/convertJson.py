import json
import model.processData as processData
from util.utilFunctions import custom_round


def convert_trip_info_to_json(processed_trips, print_count, journey_stops_by_trip, routes, taxi_first):
    result = []
    count = 1
        
    for trip_id, closest_departure_stop, closest_arrival_stop in processed_trips:
        if count > print_count:
            break
            
        trip_info = {
            "rank": count,
            "trip_id": trip_id,
            "transport_type": "버스" if str(trip_id).startswith('BR') else "지하철",
            "route_name": processData.get_route_name(trip_id, routes),
            "taxi_first": "taxi_first" if taxi_first else "walking_first",
            
            "total_journey_time": custom_round(float(closest_departure_stop['total_journey_time'].iloc[0])) if 'total_journey_time' in closest_departure_stop else None,
            
            "departure": {
                "time_to_stop": custom_round(float(closest_departure_stop['time_to_stop'].iloc[0])),
                "stop_info": {
                    "stop_id": closest_departure_stop['stop_id'].iloc[0],
                    "stop_name": closest_departure_stop['stop_name'].iloc[0],
                    "stop_lat": float(closest_departure_stop['stop_lat'].iloc[0]),
                    "stop_lon": float(closest_departure_stop['stop_lon'].iloc[0]),
                    "arrival_time": closest_departure_stop['arrival_time'].iloc[0],
                    "departure_time": closest_departure_stop['departure_time'].iloc[0],
                    "stop_sequence": int(closest_departure_stop['stop_sequence'].iloc[0]),
                    "distance_km": float(closest_departure_stop['departure_distance_km'].iloc[0])
                }
            },
            
            "arrival": {
                "time_to_stop": custom_round(float(closest_arrival_stop['time_to_stop'].iloc[0])),
                "stop_info": {
                    "stop_id": closest_arrival_stop['stop_id'].iloc[0],
                    "stop_name": closest_arrival_stop['stop_name'].iloc[0],
                    "stop_lat": float(closest_arrival_stop['stop_lat'].iloc[0]),
                    "stop_lon": float(closest_arrival_stop['stop_lon'].iloc[0]),
                    "arrival_time": closest_arrival_stop['arrival_time'].iloc[0],
                    "departure_time": closest_arrival_stop['departure_time'].iloc[0],
                    "stop_sequence": int(closest_arrival_stop['stop_sequence'].iloc[0]),
                    "distance_km": float(closest_arrival_stop['arrival_distance_km'].iloc[0])
                }
            }
        }
        
        # 경유 정류장 정보 추가
        if trip_id in journey_stops_by_trip:
            journey_stops = journey_stops_by_trip[trip_id]
            sorted_stops = sorted(journey_stops, key=lambda x: x['stop_sequence'].iloc[0])
            
            trip_info["intermediate_stops"] = [
                {
                    "stop_id": stop['stop_id'].iloc[0],
                    "stop_name": stop['stop_name'].iloc[0],
                    "stop_lat": float(stop['stop_lat'].iloc[0]),
                    "stop_lon": float(stop['stop_lon'].iloc[0]),
                    "arrival_time": stop['arrival_time'].iloc[0],
                    "departure_time": stop['departure_time'].iloc[0],
                    "stop_sequence": int(stop['stop_sequence'].iloc[0])
                }
                for stop in sorted_stops
            ]
        
        result.append(trip_info)
        count += 1
    
    json_result = json.dumps(result, ensure_ascii=False, indent=2)
     
    return json_result



