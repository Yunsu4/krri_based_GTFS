// 전역 변수로 map 선언
let map;

window.onload = function () {
    initMap(); // 서울 시청을 기준으로 지도 초기화
    setupFormHandler(); // 폼 핸들러 설정
};

// 지도 초기화 함수
function initMap() {
    var container = document.getElementById('map');
    var options = {
        center: new kakao.maps.LatLng(37.5665, 126.9780), // 서울 시청 좌표
        level: 3
    };

    map = new kakao.maps.Map(container, options);
}

// API 호출 함수
async function fetchTrips(formData) {
    try {
        if (!formData.departure_lat || !formData.departure_lon || 
            !formData.arrival_lat || !formData.arrival_lon) {
            throw new Error('모든 좌표를 입력해주세요.');
        }

        

        // 2024년 7월 1일 날짜에 입력받은 시간을 결합
        const timeValue = formData.present_time;
        const fixedDate = '2024-07-01';
        const combinedDateTime = `${fixedDate}T${timeValue}`;

        const response = await fetch('/api/trips', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                departure_lat: formData.departure_lat,
                departure_lon: formData.departure_lon,
                arrival_lat: formData.arrival_lat,
                arrival_lon: formData.arrival_lon,
                user_radius: formData.user_radius || 1,  // 기본값 설정
                arrival_radius: formData.arrival_radius || 1,  // 기본값 설정
                present_time: combinedDateTime,  // 수정된 시간 포맷
                sort_type: formData.sort_type || 'default',  // 기본값 설정
                taxi_first: formData.taxi_first || false
            })
        });

        if (!response.ok) {
            throw new Error('서버 응답 오류');
        }

        const data = await response.json();
        displayTripResults(data);  // 결과만 표시

        return data;
    } catch (error) {
        console.error('에러 발생:', error);
        throw error;
    }
}

// 마커와 폴리라인 관리를 위한 배열
let markers = [];
let polylines = []; // 폴리라인 배열 추가

// 마커와 폴리라인 초기화 함수
function clearMarkers() {
    // 마커 초기화
    markers.forEach(marker => marker.setMap(null));
    markers = [];
    
    // 폴리라인 초기화
    polylines.forEach(polyline => polyline.setMap(null));
    polylines = [];
}

// 지도에 경로 표시 함수 수정
function displayTripsOnMap(trips) {
    clearMarkers(); // 기존 마커와 폴리라인 모두 제거

    const heart_markerImage = new kakao.maps.MarkerImage(
        'static/images/custom_heart_marker.png',
        new kakao.maps.Size(30, 40)
    );

    const bus_markerImage = new kakao.maps.MarkerImage(
        'static/images/custom_bus_marker.png',
        new kakao.maps.Size(30, 40)
    );
    
    trips.forEach(trip => {
        // 출발지 마커
        const departureMarker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(
                trip.departure.stop_info.stop_lat,
                trip.departure.stop_info.stop_lon
            ),
            image: heart_markerImage,
            map: map
        });
        markers.push(departureMarker);

        // 도착지 마커
        const arrivalMarker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(
                trip.arrival.stop_info.stop_lat,
                trip.arrival.stop_info.stop_lon
            ),
            image: heart_markerImage,
            map: map
        });
        markers.push(arrivalMarker);

        // 경유 정류장 마커
        trip.intermediate_stops.forEach(stop => {
            const stopMarker = new kakao.maps.Marker({
                position: new kakao.maps.LatLng(
                    stop.stop_lat,
                    stop.stop_lon
                ),
                image: bus_markerImage,
                map: map
            });
            markers.push(stopMarker);
        });


        let linePath = [];
        
        // 출발지 좌표 추가
        linePath.push(new kakao.maps.LatLng(
            trip.departure.stop_info.stop_lat,
            trip.departure.stop_info.stop_lon
        ));
        
        // 경유지 좌표 추가
        trip.intermediate_stops.forEach(stop => {
            linePath.push(new kakao.maps.LatLng(
                stop.stop_lat,
                stop.stop_lon
            ));
        });
        
        // 도착지 좌표 추가
        linePath.push(new kakao.maps.LatLng(
            trip.arrival.stop_info.stop_lat,
            trip.arrival.stop_info.stop_lon
        ));

        // Polyline 생성
        const polyline = new kakao.maps.Polyline({
            path: linePath,
            strokeWeight: 3,
            strokeColor: '#75B8FA',
            strokeOpacity: 0.7,
            strokeStyle: 'solid'
        });
        
        // 지도에 Polyline 표시
        polyline.setMap(map);
        
        // 폴리라인 배열에 추가
        polylines.push(polyline);
    });
}

// 폼 제출 이벤트 핸들러
function setupFormHandler() {
    document.querySelector('form').addEventListener('submit', async function (e) {
        e.preventDefault();
        
        // 폼 데이터 수집
        const formData = {
            departure_lat: parseFloat(document.querySelector('[name="departure_lat"]').value),
            departure_lon: parseFloat(document.querySelector('[name="departure_lon"]').value),
            arrival_lat: parseFloat(document.querySelector('[name="arrival_lat"]').value),
            arrival_lon: parseFloat(document.querySelector('[name="arrival_lon"]').value),
            present_time: document.querySelector('[name="present_time"]').value,
            user_radius: parseInt(document.querySelector('[name="user_radius"]').value),
            arrival_radius: parseInt(document.querySelector('[name="arrival_radius"]').value),
            sort_type: document.querySelector('[name="sort_type"]').value,
            taxi_first: document.querySelector('input[name="taxi_first"]:checked').value === 'true'
        };

        // 데이터 유효성 검사
        if (isNaN(formData.departure_lat) || isNaN(formData.departure_lon) ||
        isNaN(formData.arrival_lat) || isNaN(formData.arrival_lon)) {
        throw new Error('올바른 좌표값을 입력해주세요.');
    }


        // 초기 마커만 표시
        clearMarkers();
        
        const departureMarker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(formData.departure_lat, formData.departure_lon),
            map: map
        });
        markers.push(departureMarker);

        const arrivalMarker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(formData.arrival_lat, formData.arrival_lon),
            map: map
        });
        markers.push(arrivalMarker);

        // 지도 중심을 출발지로 이동
        map.setCenter(new kakao.maps.LatLng(formData.departure_lat, formData.departure_lon));

        try {
            await fetchTrips(formData);
        } catch (error) {
            console.error('에러 발생:', error);
        }
    });
}

// 페이지 로드 시 초기화

function displayTripResults(trips) {
    const resultDiv = document.querySelector('.result');
    resultDiv.innerHTML = ''; // 기존 결과 초기화

    // rank 기준으로 정렬
    const sortedTrips = trips.sort((a, b) => a.rank - b.rank);

    sortedTrips.forEach((trip) => {
        const tripCard = document.createElement('div');
        tripCard.className = 'trip-card';
        
        tripCard.innerHTML = `
            <h3>경로 ${trip.rank} (총 소요시간: ${trip.total_journey_time}분)</h3>
            
            <div class="trip-info">
                <div class="stop-info">
                    <div class="time-info">출발: ${trip.departure.stop_info.departure_time}</div>
                    <div>출발지: ${trip.departure.stop_info.stop_name}</div>
                </div>

                <div class="stop-info">
                    <div class="bus-info">${trip.transport_type} ${trip.route_name}</div>
                    ${trip.intermediate_stops.map(stop => `
                        <div>${trip.transport_type === '버스' ? '정류장' : '정차역'}: ${stop.stop_name}</div>
                    `).join('')}
                </div>

                <div class="stop-info">
                    <div class="time-info">도착: ${trip.arrival.stop_info.arrival_time}</div>
                    <div>도착지: ${trip.arrival.stop_info.stop_name}</div>
                </div>

                <div class="distance-info">
                    ${trip.taxi_first === 'taxi_first' ? `
                        <div>택시 이동 시간: ${trip.departure.time_to_stop}분</div>
                        <div>도보 이동 시간: ${trip.arrival.time_to_stop}분</div>
                    ` : `
                        <div>도보 이동 시간: ${trip.departure.time_to_stop}분</div>
                        <div>택시 이동 시간: ${trip.arrival.time_to_stop}분</div>
                    `}
                </div>
            </div>
        `;

        // 카드 클릭 이벤트
        tripCard.addEventListener('click', () => {
            // 모든 카드의 스타일 초기화
            document.querySelectorAll('.trip-card').forEach(card => {
                card.style.backgroundColor = 'white';
            });
            // 선택된 카드 하이라이트
            tripCard.style.backgroundColor = '#e8f5e9';
            
            // 지도에 해당 경로만 표시
            clearMarkers(); // 기존 마커와 선 제거
            displayTripsOnMap([trip]); // 선택된 경로만 표시
        });

        resultDiv.appendChild(tripCard);
    });
}

