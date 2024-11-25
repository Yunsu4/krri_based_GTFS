export async function fetchTrips(formData) {
    try{
        if(!formData.departure_lat || !formData.departure_lon || 
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
                ...formData,
                user_radius: formData.user_radius || 1,  // 기본값 설정
                arrival_radius: formData.arrival_radius || 1,  // 기본값 설정
                present_time: combinedDateTime,  // 수정된 시간 포맷
                sort_type: formData.sort_type || 'default',  // 기본값 설정
                taxi_first: formData.taxi_first || false
            })
        });

        if (!response.ok) throw new Error('서버 응답 오류');

        const data = await response.json();
        return data;

    } catch (error) {
        console.error('Error fetching trips:', error);
        throw error;
    }
}
