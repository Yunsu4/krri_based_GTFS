# SetupGuide

📍 GTFS 데이터, 마커 이미지 등의 데이터는 개인이 보유하고 있다고 가정하고, 프로젝트가 구성되어 있습니다. (프로젝트 내에는 데이터가 포함되어 있지 않습니다.) 데이터를 저장하는 경로는 아래에 설명되어 있습니다.

📍 가상 환경을 만들어 pandas 등 필요한 라이브러리를 모두 세팅합니다.

### <가상 환경 구축>

가상 환경 생성 명령어:

`$python -m venv 가상환경이름`

가상 환경이 있는 디렉토리로 이동:

`$cd 가상환경이름`

가상 환경 활성화

`$ activate`

원래 디렉토리로 이동:

`$ cd ..`

\+ 이후 가상 환경을 활성화한 후 메인 디렉토리에서 필요한 라이브러리를 설치하여 사용하면 됩니다.   
설치해야 하는 라이브러리: pandas, flask, Flask-Session, redis

📍 kakao map API를 활용하였습니다. kakao Developsers 에서 app key를 발급받아 메인 디렉토리에 `config.json` 파일을 만들어 앱 키를 저장하여 사용하면 됩니다. (이외 파일은 수정하지 않아도 됩니다.)

config.json 예시

```
{
    "kakao_app_key": "본인의 앱 키"
}
```

(config.json은 `.gitignore` 파일에 넣어 보안을 유지합니다.)

📍 Redis를 세션용으로 사용하고 있습니다. docker로 redis 이미지를 만들어 실행하신 후 서버를 실행해야 합니다.

📍 static 폴더 내에 images 폴더를 만들어 마커 이미지를 보관하고, static/js/map.js에서 경로를 지정하여 사용합니다. (git에는 images 폴더가  포함되어 있지 않습니다.)

📍 raw_data라는 폴더를 만들고, `stop_times.txt` `routes.txt` 파일을 넣습니다. 

그리고 `resources` 폴더와 그 안에 `stop_times` 폴더를 만들고, `util/sliceStopTimesByHour.py`를 실행합니다. 실행 결과로 `stop_times.txt` 파일을 1시간 단위로 잘라 csv 파일로 만든 파일들이 생성됩니다.

그리고 `util/removeUnnecessaryField.py` 를 실행하여 routes.txt 에서 agency_id 필드를 삭제하고, csv 파일로 만들어 사용합니다.

`resources` 폴더 내에 `stops.txt` 파일도 넣어 사용합니다.

예시:

```java
resources/
├── stop_times/
│   └── main/
│       └── stop_times_00h.csv
│           ...stop_times_nnh.csv
├── routes.csv
├── stops.txt
```