import pandas as pd


stop_times_path = "only_land_data/stop_times.txt"
stop_times_data = pd.read_csv(stop_times_path)

# 새벽 시간대(00:00-05:00) 데이터 처리
early_morning_data = stop_times_data[
    (stop_times_data['arrival_time'] >= '24:00:00') | 
    ((stop_times_data['arrival_time'] >= '00:00:00') & 
     (stop_times_data['arrival_time'] < '05:00:00'))
]
early_morning_data.to_csv('resource/stop_times_00h.csv', index=False)
print(f"새벽 시간대(00:00-05:00) 데이터 저장 완료")


# 나머지 시간대 데이터 분리 (05:00-24:00)
for hour in range(5, 24):
    # 시작 시간과 끝 시간 설정
    start_time = f"{hour:02d}:00:00"
    end_time = f"{(hour+1):02d}:00:00"
    
    # 해당 시간대의 데이터 필터링
    hour_data = stop_times_data[
        (stop_times_data['arrival_time'] >= start_time) & 
        (stop_times_data['arrival_time'] < end_time)
    ]
    
    # 파일로 저장
    output_filename = f'resource/stop_times_{hour:02d}h.csv'
    hour_data.to_csv(output_filename, index=False)
    print(f"{hour}시 데이터 저장 완료")