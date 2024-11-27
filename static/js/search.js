import { getMap } from './map.js';

// 전역 스코프에 함수 추가
window.searchDeparture = function() {
    var keyword = document.getElementById('departure-keyword').value;
    if (!keyword.replace(/^\s+|\s+$/g, '')) {
        alert('키워드를 입력해주세요!');
        return false;
    }
    ps.keywordSearch(keyword, (data, status) => placesSearchCB(data, status, 'departure'));
}

window.searchArrival = function() {
    var keyword = document.getElementById('arrival-keyword').value;
    if (!keyword.replace(/^\s+|\s+$/g, '')) {
        alert('키워드를 입력해주세요!');
        return false;
    }
    ps.keywordSearch(keyword, (data, status) => placesSearchCB(data, status, 'arrival'));
}

// 장소 검색 객체 생성
var ps = new kakao.maps.services.Places(); 
var geocoder = new kakao.maps.services.Geocoder();

// 마커와 인포윈도우를 전역 변수로 선언
var marker = new kakao.maps.Marker();
var customOverlay = new kakao.maps.CustomOverlay({
    position: null,
    content: '',
    xAnchor: 0.5,
    yAnchor: 1.6
});

function placesSearchCB(data, status, type) {
    if (status === kakao.maps.services.Status.OK) {
        displayPlaces(data, type);
    } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
        alert('검색 결과가 존재하지 않습니다.');
    } else if (status === kakao.maps.services.Status.ERROR) {
        alert('검색 결과 중 오류가 발생했습니다.');
    }
}

function displayPlaces(places, type) {
    var listEl = document.getElementById(type + '-result');
    var fragment = document.createDocumentFragment();
    
    // 검색 결과 목록에 추가된 항목들을 제거
    removeAllChildNods(listEl);

    for (var i = 0; i < places.length; i++) {
        var itemEl = getListItem(places[i]);
        
        // 장소 클릭 이벤트
        ((place) => {
            itemEl.onclick = () => {
                // hidden input에 좌표 저장
                document.querySelector(`[name="${type}_lat"]`).value = place.y;
                document.querySelector(`[name="${type}_lon"]`).value = place.x;
                
                // 검색창에 선택된 장소 표시
                document.getElementById(type + '-keyword').value = place.place_name;
                
                // 검색 결과 목록 숨기기
                listEl.innerHTML = '';
            };
        })(places[i]);
        
        fragment.appendChild(itemEl);
    }

    listEl.appendChild(fragment);
}

function removeAllChildNods(el) {   
    while (el.hasChildNodes()) {
        el.removeChild(el.lastChild);
    }
}

function getListItem(place) {
    var el = document.createElement('div');
    el.className = 'item';

    var itemStr = `
        <h5>${place.place_name}</h5>
        ${place.road_address_name ? 
            `<span>${place.road_address_name}</span>
             <span class="jibun gray">${place.address_name}</span>` : 
            `<span>${place.address_name}</span>`}
        <span class="tel">${place.phone}</span>
    `;

    el.innerHTML = itemStr;
    return el;
}



export function initializeSearch() {
    let isDepartureFocused = false;
    let isArrivalFocused = false;

    const departureInput = document.getElementById('departure-keyword');
    const arrivalInput = document.getElementById('arrival-keyword');

    // 출발지 입력란 이벤트 리스너
    if (departureInput) {
        setupFocusListeners(departureInput, (focused) => isDepartureFocused = focused);
        
        // 엔터 키 이벤트 추가
        departureInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();  // 폼 제출 방지
                // 출발지 입력란 옆의 검색 버튼 찾기
                const searchButton = departureInput.parentElement.querySelector('button');
                if (searchButton) {
                    searchButton.click();  // 검색 버튼 클릭
                }
            }
        });
    } else {
        console.error('Departure input element not found');
    }

    // 도착지 입력란 이벤트 리스너
    if (arrivalInput) {
        setupFocusListeners(arrivalInput, (focused) => isArrivalFocused = focused);
        
        // 엔터 키 이벤트 추가
        arrivalInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();  // 폼 제출 방지
                // 도착지 입력란 옆의 검색 버튼 찾기
                const searchButton = arrivalInput.parentElement.querySelector('button');
                if (searchButton) {
                    searchButton.click();  // 검색 버튼 클릭
                }
            }
        });
    } else {
        console.error('Arrival input element not found');
    }

    const map = getMap();
    if (!map) {
        console.error('Map object not initialized');
        return;
    }

    kakao.maps.event.addListener(map, 'click', function(mouseEvent) {
        console.log('Map clicked');
        if (isDepartureFocused || isArrivalFocused) {
            console.log('Searching address for clicked location');
            searchDetailAddrFromCoords(mouseEvent.latLng, function(result, status) {
                if (status === kakao.maps.services.Status.OK) {
                    if (!result[0].road_address) {
                        alert('도로명 주소가 없습니다.');
                        return;
                    }
                    
                    const addressName = result[0].road_address.address_name || result[0].address.address_name;
                    const lat = mouseEvent.latLng.getLat();
                    const lon = mouseEvent.latLng.getLng();

                    // 마커와 인포윈도우 표시
                    displayMarkerAndInfowindow(map, mouseEvent.latLng, result[0]);

                    if (isDepartureFocused) {
                        setAddressAndCoordinates('departure', addressName, lat, lon);
                    }

                    if (isArrivalFocused) {
                        setAddressAndCoordinates('arrival', addressName, lat, lon);
                    }
                }   
            });
        }
    });
}

// 마커와 인포윈도우를 표시하는 함수
function displayMarkerAndInfowindow(map, position, result) {
    // 기존 마커 제거
    marker.setMap(null);
    customOverlay.setMap(null);

    // 마커 표시
    marker.setPosition(position);
    marker.setMap(map);

    // 커스텀 오버레이 내용 생성
    const content = createInfoWindowContent(result);
    
    // 커스텀 오버레이 표시
    customOverlay.setPosition(position);
    customOverlay.setContent(content);
    customOverlay.setMap(map);
}

// 커스텀 오버레이 내용을 생성하는 함수
function createInfoWindowContent(result) {
    return `
        <div class="infowindow-container" style="background: white; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
            ${!!result.road_address ? `
                <div class="address-row">
                    <span class="address-label">도로명</span>
                    <span class="address-content">${result.road_address.address_name}</span>
                </div>
            ` : ''}
            <div class="address-row">
                <span class="address-label">지번</span>
                <span class="address-content">${result.address.address_name}</span>
            </div>
        </div>
    `;
}

// 포커스 상태를 설정하는 함수
function setupFocusListeners(inputElement, setFocusState) {
    inputElement.addEventListener('focus', () => {
        setFocusState(true);
        console.log(`${inputElement.id} focused`);
    });

    inputElement.addEventListener('blur', () => {
        setFocusState(false);
        console.log(`${inputElement.id} blurred`);
    });
}

// 주소와 좌표를 설정하는 함수
function setAddressAndCoordinates(type, addressName, lat, lon) {
    document.getElementById(`${type}-keyword`).value = addressName;
    document.querySelector(`[name="${type}_lat"]`).value = lat;
    document.querySelector(`[name="${type}_lon"]`).value = lon;
}

// 좌표로부터 주소를 검색하는 함수
function searchDetailAddrFromCoords(coords, callback) {
    const geocoder = new kakao.maps.services.Geocoder();
    geocoder.coord2Address(coords.getLng(), coords.getLat(), callback);
}