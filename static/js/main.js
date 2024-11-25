import { initMap, clearMarkers } from "./map.js";
import { displayTripResults } from "./ui.js";
import { fetchTrips } from "./api.js";

window.onload = function() {
    initMap();
    initForm();
}

function initForm() {
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

        /*
        // 모든 마커 초기화 후 출발지 마커만 표시
        clearMarkers();
        
        const departureMarker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(formData.departure_lat, formData.departure_lon),
            map: map
        });
        markers.push(departureMarker);

        // 지도 중심을 출발지로 이동
        map.setCenter(new kakao.maps.LatLng(formData.departure_lat, formData.departure_lon));
        */

        try {
            const data = await fetchTrips(formData);
            displayTripResults(data);
        } catch (error) {
            console.error('Error fetching trips:', error);
            // 에러 발생 시에도 결과 없음 표시
            displayTripResults({ trips: [] });
        }
    });
}
