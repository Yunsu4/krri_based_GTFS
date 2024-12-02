import pandas as pd

# 전역 변수 설정
stops_file_path = "resources/stops.txt"



def load_routes():
    routes_path = "resources/routes.csv"
    return pd.read_csv(routes_path)




''' 현 시각 이후 stop_times 파일 로드(현시각이 23시 인 경우 00h까지만 로드)'''
'''
def load_stop_times(user_time):
    import os
    
    stop_times_folder = "resources/stop_times"
    hour = int(user_time.split(":")[0])
    
    # 00시부터 05시 사이인 경우 모든 파일 리턴
    if 0 <= hour < 5:
        dfs = []
        for h in range(5, 24):  # 05시부터 23시까지
            file_path = os.path.join(stop_times_folder, f"stop_times_{str(h).zfill(2)}h.csv")
            if os.path.exists(file_path):
                dfs.append(pd.read_csv(file_path))
        
        # 00시 파일 추가
        file_path = os.path.join(stop_times_folder, "stop_times_00h.csv")
        if os.path.exists(file_path):
            dfs.append(pd.read_csv(file_path))
        
        return pd.concat(dfs, ignore_index=True)
    
    # 23시인 경우 23시와 00시 데이터만 처리
    if hour == 23:
        dfs = []
        # 23시 데이터
        file_path = os.path.join(stop_times_folder, "stop_times_23h.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df = df[df['arrival_time'] >= user_time]  # 현재 시각 이후 데이터만
            dfs.append(df)
        
        # 00시 데이터
        file_path = os.path.join(stop_times_folder, "stop_times_00h.csv")
        if os.path.exists(file_path):
            dfs.append(pd.read_csv(file_path))
        
        return pd.concat(dfs, ignore_index=True)
    
    # 그 외의 경우 (현재 시각부터 23시까지 + 00시)
    dfs = []
    # 현재 시각 파일
    current_file = os.path.join(stop_times_folder, f"stop_times_{str(hour).zfill(2)}h.csv")
    if os.path.exists(current_file):
        df = pd.read_csv(current_file)
        df = df[df['arrival_time'] >= user_time]  # 현재 시각 이후 데이터만
        dfs.append(df)
    
    # 다음 시각부터 23시까지
    for h in range(hour + 1, 24):
        file_path = os.path.join(stop_times_folder, f"stop_times_{str(h).zfill(2)}h.csv")
        if os.path.exists(file_path):
            dfs.append(pd.read_csv(file_path))
    
    # 00시 데이터 추가
    file_path = os.path.join(stop_times_folder, "stop_times_00h.csv")
    if os.path.exists(file_path):
        dfs.append(pd.read_csv(file_path))
    
    return pd.concat(dfs, ignore_index=True)

'''
def load_stop_times(user_time):
    target_time = filter_target_time(user_time)

    if isinstance(target_time, str):
        stop_times_path = f"resources/stop_times/stop_times_{target_time}h.csv"
        return pd.read_csv(stop_times_path)
    else:
        first_hour_path = f"resources/stop_times/stop_times_{target_time[0]}h.csv"
        second_hour_path = f"resources/stop_times/stop_times_{target_time[1]}h.csv"

        first_hour_data = pd.read_csv(first_hour_path)
        second_hour_data = pd.read_csv(second_hour_path)

        return pd.concat([first_hour_data, second_hour_data], ignore_index=True)


def filter_target_time(user_time):
    if((user_time >= '24:00:00') | 
    ((user_time >= '00:00:00') & (user_time < '05:00:00'))):
        return "00"
    # 시간 문자열을 시, 분, 초로 분리
    hour, minute, second = user_time.split(":")

    # 분과 초가 00인지 확인
    if minute == "00" and second == "00":
        return f"{hour}"
    else:
        # 다음 시간 계산
        if hour == "23":
            next_hour = "00"
        else: next_hour = str(int(hour) + 1).zfill(2)
        return [f"{hour}", f"{next_hour}"]






"""데이터 파일들을 로드하는 함수"""
def load_data():
    stops = pd.read_csv(stops_file_path)
    routes = load_routes()
    return stops, routes

