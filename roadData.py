import pandas as pd

# 첫 5개의 데이터만 읽어오기
stop_times_path = "only_land_data/stop_times.txt"
stop_times_data = pd.read_csv(stop_times_path)
over11_stop_times = stop_times_data[stop_times_data['arrival_time'] > '23:00:00']
over11_stop_times.to_csv('over11_stop_time.csv', index=False)
print(over11_stop_times)