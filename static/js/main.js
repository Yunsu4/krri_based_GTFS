import { initMap, setMapForUserLocation } from "./map.js";
import { displayTripResults } from "./ui.js";
import { fetchTrips } from "./api.js";
import { initializeSearch } from "./search.js";
window.onload = function() {
    initMap();
    initializeSearch();
    initForm();
    setDefaultTime();
}

function setDefaultTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const currentTime = `${hours}:${minutes}`;
    document.querySelector('[name="present_time"]').value = currentTime;
}

function initForm() {
    const form = document.querySelector('form');
    const resultDiv = document.querySelector('.result');
    const loadingDiv = document.querySelector('.loading');
    let hasSearchedOnce = false;

    // 택시 순서 버튼 이벤트 리스너
    document.querySelectorAll('.taxi-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            // 활성 버튼 스타일 변경
            document.querySelectorAll('.taxi-btn').forEach(btn => 
                btn.classList.remove('active'));
            e.target.classList.add('active');
            
            // hidden input 값 업데이트
            document.querySelector('[name="taxi_first"]').value = e.target.dataset.value;

            // 이전에 검색한 적이 있고, 좌표가 모두 입력되어 있는 경우에만 자동으로 검색 실행
            const hasCoordinates = 
                document.querySelector('[name="departure_lat"]').value &&
                document.querySelector('[name="departure_lon"]').value &&
                document.querySelector('[name="arrival_lat"]').value &&
                document.querySelector('[name="arrival_lon"]').value;

            if (hasSearchedOnce && hasCoordinates) {
                // formData 직접 구성하여 API 호출
                const formData = {
                    departure_lat: parseFloat(document.querySelector('[name="departure_lat"]').value),
                    departure_lon: parseFloat(document.querySelector('[name="departure_lon"]').value),
                    arrival_lat: parseFloat(document.querySelector('[name="arrival_lat"]').value),
                    arrival_lon: parseFloat(document.querySelector('[name="arrival_lon"]').value),
                    present_time: document.querySelector('[name="present_time"]').value || setDefaultTime(),
                    taxi_first: e.target.dataset.value === 'true',
                    user_radius: e.target.dataset.value === 'true' ? 5 : 1,
                    arrival_radius: e.target.dataset.value === 'true' ? 1 : 5
                };

                try {
                    loadingDiv.style.display = 'block';
                    resultDiv.innerHTML = '';
                    
                    const data = await fetchTrips(formData);
                    setMapForUserLocation(formData.departure_lat, formData.departure_lon);
                    displayTripResults(data);
                } catch (error) {
                    console.error('Error fetching trips:', error);
                    displayTripResults({ trips: [] });
                } finally {
                    loadingDiv.style.display = 'none';
                }
            }
        });
    });

    // 폼 제출 이벤트 리스너
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        
        loadingDiv.style.display = 'block';
        resultDiv.innerHTML = '';
        
        const formData = {
            departure_lat: parseFloat(document.querySelector('[name="departure_lat"]').value),
            departure_lon: parseFloat(document.querySelector('[name="departure_lon"]').value),
            arrival_lat: parseFloat(document.querySelector('[name="arrival_lat"]').value),
            arrival_lon: parseFloat(document.querySelector('[name="arrival_lon"]').value),
            present_time: document.querySelector('[name="present_time"]').value || setDefaultTime(),
            taxi_first: document.querySelector('[name="taxi_first"]').value === 'true',
            user_radius: document.querySelector('[name="taxi_first"]').value === 'true' ? 5 : 1,
            arrival_radius: document.querySelector('[name="taxi_first"]').value === 'true' ? 1 : 5
        };

        try {
            const data = await fetchTrips(formData);
            setMapForUserLocation(formData.departure_lat, formData.departure_lon);
            displayTripResults(data);
            hasSearchedOnce = true;
        } catch (error) {
            console.error('Error fetching trips:', error);
            displayTripResults({ trips: [] });
        } finally {
            loadingDiv.style.display = 'none';
        }
    });
}
