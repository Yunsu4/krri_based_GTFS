import { clearMarkers, displayTripsOnMap } from "./map.js";
import { fetchTrips } from "./api.js";

let currentData = null;

export function displayTripResults(data) {
    currentData = {
        ...data,
        present_time: data.present_time || document.querySelector('[name="present_time"]').value
    };
    
    const sortButtons = document.querySelector('.sort-buttons');
    
    if (!data || !data.trips || data.trips.length === 0) {
        sortButtons.style.display = 'none';
    } else {
        sortButtons.style.display = 'flex';
        
        if (!window.sortButtonsInitialized) {
            initSortButtons();
            window.sortButtonsInitialized = true;
            document.querySelector('.sort-btn[data-sort="default"]').classList.add('active');
        }
    }
    
    displaySortedTrips(data);
}

function initSortButtons() {
    document.querySelectorAll('.sort-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            document.querySelectorAll('.sort-btn').forEach(btn => 
                btn.classList.remove('active'));
            e.target.classList.add('active');
            
            const loadingDiv = document.querySelector('.loading');
            const resultDiv = document.querySelector('.result');
            loadingDiv.style.display = 'block';
            resultDiv.innerHTML = '';
            
            try {
                const taxiFirst = document.querySelector('[name="taxi_first"]').value === 'true';
                
                const formData = {
                    departure_lat: currentData.user_coordinates.departure_lat,
                    departure_lon: currentData.user_coordinates.departure_lon,
                    arrival_lat: currentData.user_coordinates.arrival_lat,
                    arrival_lon: currentData.user_coordinates.arrival_lon,
                    present_time: currentData.present_time,
                    taxi_first: taxiFirst,
                    user_radius: taxiFirst ? 5 : 1,
                    arrival_radius: taxiFirst ? 1 : 5,
                    sort_type: e.target.dataset.sort
                };

                const data = await fetchTrips(formData);
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

        tripCard.addEventListener('click', () => {
            document.querySelectorAll('.trip-card').forEach(card => {
                card.style.backgroundColor = 'white';
            });
            tripCard.style.backgroundColor = '#e8f5e9';
            
            clearMarkers();
            displayTripsOnMap({trips: [trip], user_coordinates: data.user_coordinates});
        });

        resultDiv.appendChild(tripCard);
    });
}
