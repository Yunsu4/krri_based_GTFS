import { initMap, setMapForUserLocation } from "./map.js";
import { displayTripResults } from "./ui.js";
import { fetchTrips } from "./api.js";

window.onload = function() {
    initMap();
    initForm();
}

function initForm() {
    const form = document.querySelector('form');
    const resultDiv = document.querySelector('.result');
    const loadingDiv = document.querySelector('.loading');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        
        // 로딩 표시 시작
        loadingDiv.style.display = 'block';
        resultDiv.innerHTML = ''; // 기존 결과 초기화
        
        const taxiFirst = document.querySelector('input[name="taxi_first"]:checked').value === 'true';
        
        // 입력 데이터 수집
        const formData = {
            departure_lat: parseFloat(document.querySelector('[name="departure_lat"]').value),
            departure_lon: parseFloat(document.querySelector('[name="departure_lon"]').value),
            arrival_lat: parseFloat(document.querySelector('[name="arrival_lat"]').value),
            arrival_lon: parseFloat(document.querySelector('[name="arrival_lon"]').value),
            present_time: document.querySelector('[name="present_time"]').value,
            taxi_first: taxiFirst,
            user_radius: taxiFirst ? 5 : 1,
            arrival_radius: taxiFirst ? 1 : 5
        };

        try {
            const data = await fetchTrips(formData);
            setMapForUserLocation(formData.departure_lat, formData.departure_lon);
            displayTripResults(data);
        } catch (error) {
            console.error('Error fetching trips:', error);
            displayTripResults({ trips: [] });
        } finally {
            // 로딩 표시 종료
            loadingDiv.style.display = 'none';
        }
    });
}
