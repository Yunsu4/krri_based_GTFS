import { clearMarkers, displayTripsOnMap } from "./map.js";
import { fetchTrips } from "./api.js";

let currentData = null;

export function displayTripResults(data) {
    currentData = data;
    
    const sortButtons = document.querySelector('.sort-buttons');
    
    if (!data || !data.trips || data.trips.length === 0) {
        // 검색 결과가 없으면 정렬 버튼 숨김
        sortButtons.style.display = 'none';
    } else {
        // 검색 결과가 있으면 정렬 버튼 표시
        sortButtons.style.display = 'flex';
        
        // 정렬 버튼 초기화 (처음 한 번만)
        if (!window.sortButtonsInitialized) {
            initSortButtons();
            window.sortButtonsInitialized = true;
            
            // 처음 검색 시에만 시간순 버튼 활성화
            document.querySelector('.sort-btn[data-sort="default"]').classList.add('active');
        }
    }
    
    displaySortedTrips(data);
}

function initSortButtons() {
    document.querySelectorAll('.sort-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            // 활성 버튼 스타일 변경
            document.querySelectorAll('.sort-btn').forEach(btn => 
                btn.classList.remove('active'));
            e.target.classList.add('active');
            
            // 로딩 표시 시작
            const loadingDiv = document.querySelector('.loading');
            const resultDiv = document.querySelector('.result');
            loadingDiv.style.display = 'block';
            resultDiv.innerHTML = ''; // 기존 결과 초기화
            
            // 현재 폼 데이터 가져오기
            const taxiFirst = document.querySelector('input[name="taxi_first"]:checked').value === 'true';
            
            const formData = {
                departure_lat: parseFloat(document.querySelector('[name="departure_lat"]').value),
                departure_lon: parseFloat(document.querySelector('[name="departure_lon"]').value),
                arrival_lat: parseFloat(document.querySelector('[name="arrival_lat"]').value),
                arrival_lon: parseFloat(document.querySelector('[name="arrival_lon"]').value),
                present_time: document.querySelector('[name="present_time"]').value,
                taxi_first: taxiFirst,
                user_radius: taxiFirst ? 2 : 1,
                arrival_radius: taxiFirst ? 1 : 2,
                sort_type: e.target.dataset.sort
            };

            try {
                const data = await fetchTrips(formData);
                displayTripResults(data);
            } catch (error) {
                console.error('Error fetching sorted trips:', error);
                displayTripResults({ trips: [] });
            } finally {
                // 로딩 표시 종료
                loadingDiv.style.display = 'none';
            }
        });
    });
}

function displaySortedTrips(data) {
    const resultDiv = document.querySelector('.result');
    resultDiv.innerHTML = '';

    if (!data || !data.trips || data.trips.length === 0) {
        const noResultCard = document.createElement('div');
        noResultCard.className = 'trip-card no-result';
        noResultCard.innerHTML = `
            <h3>탐색 결과 경로가 없습니다.</h3>
        `;
        resultDiv.appendChild(noResultCard);
        return;
    }

    data.trips.forEach((trip) => {
        const tripCard = document.createElement('div');
        tripCard.className = 'trip-card';
        
        // intermediate_stops가 있는지 확인하고 없으면 빈 배열 사용
        const intermediateStopsHtml = trip.intermediate_stops ? 
            trip.intermediate_stops.map(stop => `
                <div>${trip.transport_type === '버스' ? '정류장' : '정차역'}: ${stop.stop_name}</div>
            `).join('') : '';
        
        tripCard.innerHTML = `
            <h3>경로 ${trip.rank} (총 소요시간: ${trip.total_journey_time}분)</h3>
            
            <div class="trip-info">
                <div class="stop-info">
                    <div class="time-info">출발: ${trip.departure.stop_info.departure_time}</div>
                    <div>출발지: ${trip.departure.stop_info.stop_name}</div>
                </div>

                <div class="stop-info">
                    <div class="bus-info">${trip.transport_type} ${trip.route_name}</div>
                    ${intermediateStopsHtml}
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
            displayTripsOnMap({trips: [trip], user_coordinates: data.user_coordinates}); // 선택된 경로만 표시
        });

        resultDiv.appendChild(tripCard);
    });
}
