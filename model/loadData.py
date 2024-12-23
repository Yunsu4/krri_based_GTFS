import pandas as pd

# 전역 변수 설정
stops_file_path = "resources/stops.txt"

"""데이터 파일들을 로드하는 함수"""

def load_routes():
    routes_path = "resources/routes.csv"
    return pd.read_csv(routes_path)


def load_stops_data():
    stops = pd.read_csv(stops_file_path)
    return stops


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
