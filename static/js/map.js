let map;
let markers = [];
let polylines = [];


// 지도 초기화
export function initMap() {
    const container = document.getElementById('map');
    const options = {
        center: new kakao.maps.LatLng(37.312651, 126.952781), // 철도연 좌표
        level: 3
    };
    map = new kakao.maps.Map(container, options);
}

// 마커와 폴리라인 초기화
export function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];

    polylines.forEach(polyline => polyline.setMap(null));
    polylines = [];
}

// 지도에 경로 표시
export function displayTripsOnMap(data) {
    clearMarkers();

    const heart_markerImage = new kakao.maps.MarkerImage(
        'static/images/custom_heart_marker.png',
        new kakao.maps.Size(30, 40)
    );

    const bus_markerImage = new kakao.maps.MarkerImage(
        'static/images/custom_bus_marker.png',
        new kakao.maps.Size(30, 40)
    );

    const userCoords = data.user_coordinates;

    data.trips.forEach(trip => {
        // 현위치 마커
        createMarker(userCoords.departure_lat, userCoords.departure_lon, heart_markerImage, map);

        // 목적지 마커
        createMarker(userCoords.arrival_lat, userCoords.arrival_lon, heart_markerImage, map);

        // 출발 정류장 마커
        createMarker(
            trip.departure.stop_info.stop_lat, trip.departure.stop_info.stop_lon,
            bus_markerImage, map
        );

        // 도착 정류장 마커
        createMarker(
            trip.arrival.stop_info.stop_lat, trip.arrival.stop_info.stop_lon,
            bus_markerImage, map
        );

        // 경유 정류장 마커
        trip.intermediate_stops.forEach(stop => {
            createMarker(stop.stop_lat, stop.stop_lon, bus_markerImage, map);
        });

        // polyline 설정

        // 실제 출발지 -> 출발 정류장 연결선
        const startConnectionPath = [
            new kakao.maps.LatLng(userCoords.departure_lat, userCoords.departure_lon),
            new kakao.maps.LatLng(trip.departure.stop_info.stop_lat, trip.departure.stop_info.stop_lon)
        ];        
        createPolyline(startConnectionPath, '#FF0000', 'dashed');

        // 도착 정류장 -> 실제 도착지 연결선
        const endConnectionPath = [
            new kakao.maps.LatLng(trip.arrival.stop_info.stop_lat, trip.arrival.stop_info.stop_lon),
            new kakao.maps.LatLng(userCoords.arrival_lat, userCoords.arrival_lon)
        ];        
        createPolyline(endConnectionPath, '#FF0000', 'dashed');

        const linePath = [
            new kakao.maps.LatLng(trip.departure.stop_info.stop_lat, trip.departure.stop_info.stop_lon),
            ...trip.intermediate_stops.map(stop => new kakao.maps.LatLng(stop.stop_lat, stop.stop_lon)),
            new kakao.maps.LatLng(trip.arrival.stop_info.stop_lat, trip.arrival.stop_info.stop_lon),
        ];
        createPolyline(linePath, '#75B8FA', 'solid');

        // 모든 좌표를 포함하는 영역 생성
        const bounds = new kakao.maps.LatLngBounds();
        
        // 모든 좌표를 bounds에 추가
        bounds.extend(new kakao.maps.LatLng(userCoords.departure_lat, userCoords.departure_lon));
        bounds.extend(new kakao.maps.LatLng(userCoords.arrival_lat, userCoords.arrival_lon));
        bounds.extend(new kakao.maps.LatLng(trip.departure.stop_info.stop_lat, trip.departure.stop_info.stop_lon));
        bounds.extend(new kakao.maps.LatLng(trip.arrival.stop_info.stop_lat, trip.arrival.stop_info.stop_lon));
        trip.intermediate_stops.forEach(stop => {
            bounds.extend(new kakao.maps.LatLng(stop.stop_lat, stop.stop_lon));
        });

        // 지도 영역 설정
        map.setBounds(bounds);
    });
}

// 마커 생성 함수
function createMarker(lat, lon, image, map) {
    const marker = new kakao.maps.Marker({
        position: new kakao.maps.LatLng(lat, lon),
        image: image,
        map: map,
    });
    markers.push(marker);
    //return marker; // 필요시 사용
}


// 폴리라인 생성 함수
function createPolyline(path, color = '#75B8FA', style = 'solid') {
    const polyline = new kakao.maps.Polyline({
        path: path,
        strokeWeight: 3,
        strokeColor: color,
        strokeOpacity: 0.7,
        strokeStyle: style,
    });
    polyline.setMap(map);
    polylines.push(polyline);
}

