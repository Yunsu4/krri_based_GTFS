# <구현 목표>

1. 택시 나중에 탑승: 현 위치에서 1km 내의 버스 정류장까지 걸어가서 버스를 타고, 이후 목적지 5km 내에서 택시를 타는 방법
2. 택시 먼저 탑승: 현 위치에서 5km 내에 위치한 버스 정류장까지 택시를 타고 도착하여 버스를 타고 목적지 1km 내에서 내려서 목적지까지 걸어가는 방법 

<br>
<br>
<br>

# <참고 사항>

### ❗현재 "for_new_gtfs" branch는 버스 데이터만 포함된 GTFS를 기준으로 구성되어 있습니다.
("web_final"와 `processData.py`, `ui,js` 파일의 일부 코드가 변형된 버전입니다.) 


📍 모든 기능은 구현 과정정의 번호 순서대로 [`processData.py`] 내에 구현되어 있습니다.

### 프로젝트 구조

```markdown
project-root/
├── docs/
│   ├── Api.md
│   └── Setup.md
├── controller/
│   └── tripsController.py
├── model/
│   ├── loadData.py
│   ├── processData.py
│   └── convertJson.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js
│       ├── main.js
│       ├── map.js
│       ├── search.js
│       └── ui.js
├── templates/
│   └── index.html
├── util/
│   ├── removeUnnecessaryField.py
│   ├── sliceFile.py
│   └── utilFunctions.py
├── app.py
└── README.md
```

📍 clone 후 처음 프로젝트를 실행할 때에는 docs/Setup.md 파일을 참고하여 환경과 데이터 설정을 해야 합니다.

📍 00시부터 04:59분까지 시간표 정보는 모두 stop_times_00h.csv에 포함되어 있습니다.

예시) 11시 데이터 → stop_times_23h.csv, 00시 ~ 04시 데이터 → stop_times_00h.csv, 05시 데이터 → stop_times_05h.csv

<br>
<br>
<br>


# <구현 과정 - 구현 목표 1, 2 모두 적용 가능>

**<출발 정류장>**

1. 현 위치 반경 직선 거리 nkm 내 정류장 n개 추출(성능을 위해 최대 100개로 제한)
2. [보정] 현재 시간 이후에도 운영하는 버스만 매칭

<br>

**<도착 정류장>**

1. 목적지 반경 직선 거리 nkm내 버스 정류장 n개 추출(성능을 위해 최대 100개로 제한)
2. [보정] 현재 시간 이후에도 운영하는 버스만 매칭

→ 출발 정류장과 도착 정류장의 반경 직선 거리 n은 택시를 타고 이동하는 경우 5, 도보 이동의 경우 1로 설정

예시) 택시 먼저 탑승: 출발 정류장 반경 5km, 도착 정류장 1km 탐색

택시 나중에 탑승: 출발 정류장 반경 1km, 도착 정류장 5km 탐색

<br>

**<출발 정류장과 도착 정류장이 노선으로 연결되어 있는 경우 추출>**

1. 출발지와 도착지가 경로로 이어져 있는 경우 추출

<br>

**<보정 - 출발 정류장의 버스 출발 시간 기준, 노선과 현 시각 매칭>**

1. 출발 정류장의 버스 출발 시간을 기준으로 정렬
2. 현 위치에서 출발 정류장까지 **걸어가는 시간** or **택시로 이동하는 시간** 계산, 정류장까지 이동하여 도착한 시간 이후에 운영하는 버스 매칭
- 걸어가는 경우: 1km에 15분 이동으로 계산
- 택시로 이동하는 경우: 시속 60km/h로 보아 1km에 1분 이동으로 계산
1. 출발 정류장의 버스 출발 시간 보다 늦게 도착하는 도착 정류장 버스만 필터링

<br>

**<보정 - 현 위치와 정류장, 목적지와 정류장 사이의 거리 기준>**

1. 각 노선을 순회하면서 출발지와 가장 가까운 정류장을 출발 정류장으로, 도착지와 가장 가까운 정류장을 도착 정류장으로 설정 
2. 도착 정류장에서 목적지까지 **걸어가는 시간** or **택시로 이동하는 시간** 계산

→ 정렬된 노선 중 10개만 추출

<br>

**<기준에 따른 정렬>**

- 기본 값: 가장 빨리 탈 수 있는 대중교통
- 정렬 기준 1. 총 소요 시간

→  정류장까지 가는 데 걸리는 시간+ 버스 이용 시간 + 도착 정류장에서 목적지까지 가는데 걸리는 시간 합산 후 가장 짧은 시간으로 비교

- 정렬 기준 2. 택시 이동 거리
- 정렬 기준 3. 걸어가는 거리

⇒ 정렬 기준이 되는 값이 동일한 경우 버스 출발 시간이 빠른 순서대로(기본 값) 정렬한다.

1. [보정] 동일한 노선의 버스가 중복 표시되지 않도록 필터링

<br>

**<경로 구하기>**

1. 경유하는 정류장을 모두 출력하여 경로를 구한다.
2. 노선 이름을 조회하여 출력한다.

→ 최종 경로는 최대 10개만 출력한다.