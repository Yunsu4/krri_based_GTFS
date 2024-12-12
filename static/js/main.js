import { initMap, setMapForUserLocation } from "./map.js";
import { displayTripResults } from "./ui.js";
import { fetchTrips } from "./api.js";
import { initializeSearch } from "./search.js";


// 페이지 로드 시 지도, 검색, 폼, 현재 시간 초기화
window.onload = function() {
    initMap();
    initializeSearch();
    initForm();
    setDefaultTime();
}


// 현재 시간 설정(HH:MM)
function setDefaultTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const currentTime = `${hours}:${minutes}`;
    document.querySelector('[name="present_time"]').value = currentTime;
    return currentTime;
}


// 폼 초기화
function initForm() {
    const form = document.querySelector('form');
    const resultDiv = document.querySelector('.result');
    const loadingDiv = document.querySelector('.loading');
    let hasSearchedOnce = false;
    let lastFormData = null;  // 마지막 검색에 사용된 formData 저장

    // 폼 제출 이벤트 리스너 (첫 검색)
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        
        loadingDiv.style.display = 'block';
        resultDiv.innerHTML = '';
        
        lastFormData = {  // formData 저장
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
            const data = await fetchTrips(lastFormData);
            setMapForUserLocation(lastFormData.departure_lat, lastFormData.departure_lon);
            displayTripResults(data);
            hasSearchedOnce = true;  // 첫 검색 완료 표시
        } catch (error) {
            console.error('Error fetching trips:', error);
            displayTripResults({ trips: [] });
        } finally {
            loadingDiv.style.display = 'none';
        }
    });

    // 택시 순서 버튼 이벤트 리스너 (이후 검색)
    document.querySelectorAll('.taxi-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            if (!hasSearchedOnce || !lastFormData) return;  // 첫 검색 전이면 무시

            document.querySelectorAll('.taxi-btn').forEach(btn => 
                btn.classList.remove('active'));
            e.target.classList.add('active');
            
            document.querySelector('[name="taxi_first"]').value = e.target.dataset.value;

            // 저장된 formData 사용하고 필요한 값만 업데이트
            lastFormData.taxi_first = e.target.dataset.value === 'true';
            lastFormData.user_radius = e.target.dataset.value === 'true' ? 5 : 1;
            lastFormData.arrival_radius = e.target.dataset.value === 'true' ? 1 : 5;

            try {
                loadingDiv.style.display = 'block';
                resultDiv.innerHTML = '';
                
                const data = await fetchTrips(lastFormData);
                setMapForUserLocation(lastFormData.departure_lat, lastFormData.departure_lon);
                displayTripResults(data);
            } catch (error) {
                console.error('Error fetching trips:', error);
                displayTripResults({ trips: [] });
            } finally {
                loadingDiv.style.display = 'none';
            }
        });
    });

    document.querySelectorAll('.sort-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            if(!hasSearchedOnce || !lastFormData) {
                console.error('데이터가 없습니다.');
                return;
            }

            loadingDiv.style.display = 'block';
            resultDiv.innerHTML = '';

            try{
                // 이전 검색 결과에서 필요한 데이터만 가져오기
                const formData = {
                    ...lastFormData,
                    sort_type: e.target.dataset.sort
                };

                const data = await fetchTrips(formData);
                setMapForUserLocation(lastFormData.departure_lat, lastFormData.departure_lon);
                displayTripResults(data);
            } catch (error) {
                console.error('Error fetching sorted trips:', error);
                displayTripResults({ trips: [] });
            } finally {
                loadingDiv.style.display = 'none';
            }
        });
    });
}
