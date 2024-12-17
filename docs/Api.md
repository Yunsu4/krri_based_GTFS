# Api 명세서

 [[Api 명세서 노션](https://www.notion.so/API-15e12d4b1dd4806ebc27c209d5b40d98?pvs=4)]
 (내용은 거의 동일합니다.)

<br>

## 1. 홈 페이지 렌더링

Endpoint: `/`

Method: GET

- 홈 페이지를 렌더링하고 `kakao_app_key`를 포함해 클라이언트에 전달합니다. (`kakao_app_key`의 경우 서버측에 포함되어 있으므로 바로 렌더링 가능합니다.)

<br>
<br>
<br>

## 2. 경로 조회 및 정렬

Endpoint: `/api/trips`

Method: POST

- **POST** 요청 시 사용자 입력 조건에 맞는 경로를 조회하거나 정렬합니다.
- 이전에 검색한 데이터와 새로운 조건을 비교해 기존 데이터를 재사용할지, 새로 검색할지를 결정합니다.

<br>


### **Request Body**

| Key | Type | 필수 여부 | 설명 |
| --- | --- | --- | --- |
| departure_lat | Float | Yes | 출발지 위도 |
| departure_lon | Float | Yes | 출발지 경도 |
| arrival_lat | Float | Yes | 목적지 위도 |
| arrival_lon | Float | Yes | 목적지 경도 |
| user_radius | Integer | Yes | 사용자 출발 반경 |
| arrival_radius | Integer | Yes | 도착 반경 |
| present_time | String | Yes | 현재 시간 (ISO 포맷) |
| sort_type | String | No | 정렬 기준 (default 값 사용 가능) |
| taxi_first | Boolean | No | 택시 우선 여부 (True/False, deault: true) |

<br>


### Requset Body 필드와 웹 브라우저 동작 매핑

- **user_radius, arrival_radius, taxi_first**

웹 서비스에서 사용자가 `택시 먼저 탑승` 을 선택하면 taxi_first는 true, user_radius는 5, arrival_radius는 1로 설정됩니다.

`택시 나중에 탑승` 을 선택하면 taxi_first는 false, user_radius는 1, arrival_radius는 5로 설정됩니다.

- **sort_type**

웹 서비스에서 사용자가 새로운 경로를 검색할 경우 `sort_type` 은 `default` 로 설정됩다.

경로가 탐색된 후 `시간순` , `총 소요시간순` , `도보 거리순` , `택시 거리순` 중 하나를 선택할 경우 세션에 저장된 데이터를 기반으로 `Request Body` 의 필드가 채워지고, `sort_type` 필드만 사용자의 선택에 따라 입력됩니다.

<br>


### Request 예시

```json
{
    "departure_lat": 37.31233179887807,
    "departure_lon": 126.95661633750534,
    "arrival_lat": 37.2657903079673,
    "arrival_lon": 127.000094700292,
    "user_radius": 5,
    "arrival_radius": 1,
    "present_time": "2024-07-01T10:19",
    "sort_type": "default",
    "taxi_first": true
}
```

<br>


### **Response Body**

| Key | Type | 설명 |
| --- | --- | --- |
| trips | List[Object] | 여행 경로 결과 리스트 |
| user_coordinates | Object | 사용자가 입력한 출/도착 좌표 |

<br>


### **Response 예시 (일부 발췌)**
```json
{
	 "trips": [
        {
            "arrival": {
                "stop_info": {
                    "arrival_time": "10:54:57",
                    "departure_time": "10:55:07",
                    "distance_km": 0.2588013398193875,
                    "stop_id": "BS_3100_202000208",
                    "stop_lat": 37.26808,
                    "stop_lon": 126.99957,
                    "stop_name": "수원역.노보텔수원",
                    "stop_sequence": 114
                },
                "time_to_stop": 4
            },
            "departure": {
                "stop_info": {
                    "arrival_time": "10:38:42",
                    "departure_time": "10:38:52",
                    "distance_km": 1.4601025809155075,
                    "stop_id": "BS_3100_201000460",
                    "stop_lat": 37.29963,
                    "stop_lon": 126.95243,
                    "stop_name": "서수원레이크푸르지오2단지",
                    "stop_sequence": 103
                },
                "time_to_stop": 1
            },
            "intermediate_stops": [
                {
                    "arrival_time": "10:40:20",
                    "departure_time": "10:40:30",
                    "stop_id": "BS_3100_201000312",
                    "stop_lat": 37.29763,
                    "stop_lon": 126.958,
                    "stop_name": "웅비아파트",
                    "stop_sequence": 104,
                    "trip_id": "BR_3100_200000070_Ord016"
                },
                ...
                {
                    "arrival_time": "10:51:21",
                    "departure_time": "10:51:31",
                    "stop_id": "BS_3100_201000033",
                    "stop_lat": 37.27337,
                    "stop_lon": 126.98423,
                    "stop_name": "더함파크",
                    "stop_sequence": 112,
                    "trip_id": "BR_3100_200000070_Ord016"
                }
            ],
            "rank": 3,
            "route_name": "11-1",
            "taxi_first": "taxi_first",
            "total_journey_time": 21,
            "transport_type": "버스",
            "trip_id": "BR_3100_200000070_Ord016"
        }
    ],
    "user_coordinates": {
        "arrival_lat": 37.2657903079673,
        "arrival_lon": 127.000094700292,
        "departure_lat": 37.31233179887807,
        "departure_lon": 126.95661633750534
    }
}
```