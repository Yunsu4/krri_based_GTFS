import { clearMarkers, displayTripsOnMap } from "./map.js";

export function displayTripResults(data) {
    const resultDiv = document.querySelector('.result');
    resultDiv.innerHTML = '';

    // 데이터가 없거나 trips가 비어있는 경우 처리
    if (!data || !data.trips || data.trips.length === 0) {
        const noResultCard = document.createElement('div');
        noResultCard.className = 'trip-card no-result';
        noResultCard.innerHTML = `
            <h3>탐색 결과 경로가 없습니다.</h3>
        `;
        resultDiv.appendChild(noResultCard);
        return;
    }

    // rank 기준으로 정렬
    const sortedTrips = data.trips.sort((a, b) => a.rank - b.rank);

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
            displayTripsOnMap({trips: [trip], user_coordinates: data.user_coordinates}); // 선택된 경로만 표시
        });

        resultDiv.appendChild(tripCard);
    });
}
