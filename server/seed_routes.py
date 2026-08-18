"""
mockData.js 의 ROUTES_MOCK 데이터를 DB로 이관하는 1회성 시드 스크립트.

사용법 (프로젝트 루트, main.py와 같은 위치에서 실행):
    python seed_routes.py

이미 존재하는 id는 건너뛰므로 여러 번 실행해도 안전합니다.
"""

from database.connection import SessionLocal, engine, Base
from models.routes_model import RouteModel, RouteStationStatusModel

# mockData.js 의 ROUTES_MOCK 을 그대로 옮긴 데이터.
# station: (departure_name, departure_available, departure_total, destination_name, destination_available, destination_total)
ROUTES_SEED = [
    {
        "id": "bukhansan-loop",
        "name": "북한산 순환 코스",
        "region": "서울 · 은평구",
        "region_tag": "서울",
        "difficulty": "고급",
        "bike_type": "MTB",
        "distance": "42km",
        "duration": "3h 20m",
        "rating": 4.9,
        "review_count": 1284,
        "image": "https://images.unsplash.com/photo-1633707167699-cdd893b84441?w=1200&q=70",
        "tags": ["고급", "MTB"],
        "elevation_gain": "1,240m",
        "max_elevation": "1,240m",
        "completion_rate": 78,
        "participants": 3082,
        "season": "봄 · 가을",
        "description": "북한산 국립공원을 순환하는 험준한 산악 코스. 가파른 오르막과 시원한 내리막이 반복되는 스릴 만점의 루트.",
        "safety_tips": [
            "헬멧과 보호대를 반드시 착용하세요",
            "출발 전 GPS와 배터리를 확인하세요",
            "날씨 변화에 대비한 레이어를 준비하세요",
            "초행길은 혼자보다 그룹 라이딩을 추천해요",
        ],
        "elevation_profile": [
            {"km": 0, "elevation": 80}, {"km": 8, "elevation": 420}, {"km": 16, "elevation": 980},
            {"km": 21, "elevation": 1240}, {"km": 28, "elevation": 1100}, {"km": 35, "elevation": 650},
            {"km": 42, "elevation": 90},
        ],
        "station": None,
    },
    {
        "id": "hangang-yeouinaru-hapjeong",
        "name": "여의나루-합정 한강 코스",
        "region": "서울 · 영등포 · 마포",
        "difficulty": "입문",
        "bike_type": "따릉이",
        "distance": "8.2km",
        "duration": "35분",
        "rating": 4.8,
        "review_count": 2840,
        "image": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=1200&q=70",
        "tags": ["AI 추천", "입문"],
        "free": True,
        "description": "한강변 자전거도로를 따라 달리는 서울 대표 따릉이 코스. 평탄한 지형으로 누구나 편하게 즐길 수 있습니다.",
        "station": ("여의나루역 1번출구", 14, 20, "합정역 6번출구", 2, 20),
    },
    {
        "id": "ttukseom-jamsil",
        "name": "뚝섬-잠실 한강 코스",
        "region": "서울 · 성동 · 송파",
        "difficulty": "입문",
        "bike_type": "따릉이",
        "distance": "12.4km",
        "duration": "55분",
        "rating": 4.7,
        "image": "https://images.unsplash.com/photo-1541625602330-2277a4c46182?w=1200&q=70",
        "tags": ["입문"],
        "free": True,
        "station": ("뚝섬유원지역 1번출구", 8, 15, "잠실역 5번출구", 11, 15),
    },
    {
        "id": "banpo-ichon",
        "name": "반포-이촌 한강 코스",
        "region": "서울 · 서초 · 용산",
        "difficulty": "입문",
        "bike_type": "따릉이",
        "distance": "6.8km",
        "duration": "28분",
        "rating": 4.6,
        "image": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=1200&q=70",
        "tags": ["입문"],
        "free": True,
        "station": ("반포한강공원 동측", 0, 12, "이촌한강공원 앞", 9, 12),
    },
    {
        "id": "seongsu-cafe",
        "name": "성수 카페거리 순환",
        "region": "서울 · 성동",
        "difficulty": "입문",
        "bike_type": "따릉이",
        "distance": "5.2km",
        "duration": "25분",
        "rating": 4.5,
        "image": "https://images.unsplash.com/photo-1519677100203-a0e668c92439?w=1200&q=70",
        "tags": ["입문"],
        "free": True,
        "station": ("성수역 4번출구", 12, 15, "성수역 4번출구", 12, 15),
    },
    {
        "id": "namsan-loop",
        "name": "남산 순환 코스",
        "region": "서울 · 중구",
        "difficulty": "중급",
        "bike_type": "따릉이",
        "distance": "4.8km",
        "duration": "30분",
        "rating": 4.7,
        "image": "https://images.unsplash.com/photo-1465447142348-e9952c393450?w=1200&q=70",
        "tags": ["중급"],
        "free": True,
        "station": ("회현역 5번출구", 7, 10, "회현역 5번출구", 7, 10),
    },
    {
        "id": "hangang-full",
        "name": "한강 종주 라이딩",
        "region": "서울 · 전 구간",
        "region_tag": "서울",
        "difficulty": "중급",
        "bike_type": "로드",
        "distance": "132km",
        "duration": "6h 45m",
        "elevation_gain": "380m",
        "rating": 4.8,
        "review_count": 3412,
        "image": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=1200&q=70",
        "tags": ["오늘의 추천", "중급"],
        "description": "서울 전 구간을 가로지르는 한강 자전거 전용도로. 평탄한 지형으로 초보자도 도전 가능한 서울 대표 라이딩 코스입니다.",
        "station": None,
    },
    {
        "id": "jeju-ring-road",
        "name": "제주 환상 자전거길",
        "region": "제주 · 전도",
        "region_tag": "제주",
        "difficulty": "도전",
        "bike_type": "투어링",
        "distance": "234km",
        "duration": "2박 3일",
        "elevation_gain": "2,850m",
        "rating": 5,
        "review_count": 892,
        "image": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=1200&q=70",
        "tags": ["도전", "투어링"],
        "station": None,
    },
    {
        "id": "namsan-circuit",
        "name": "남산 순환 코스",
        "region": "서울 · 중구",
        "region_tag": "서울",
        "difficulty": "입문",
        "bike_type": "도심",
        "distance": "8km",
        "duration": "45분",
        "elevation_gain": "240m",
        "rating": 4.6,
        "review_count": 2150,
        "image": "https://images.unsplash.com/photo-1465447142348-e9952c393450?w=1200&q=70",
        "tags": ["입문", "도심"],
        "station": None,
    },
    {
        "id": "busan-galmaetgil",
        "name": "부산 갈맷길 해안 코스",
        "region": "부산 · 해운대 ~ 송정",
        "region_tag": "부산",
        "difficulty": "중급",
        "bike_type": "로드",
        "distance": "55km",
        "duration": "4h 10m",
        "elevation_gain": "680m",
        "rating": 4.7,
        "review_count": 976,
        "image": "https://images.unsplash.com/photo-1744802093072-dad02dd5b79d?w=1200&q=70",
        "tags": ["중급", "로드"],
        "station": None,
    },
    {
        "id": "gyeongin-arabetgil",
        "name": "경인 아라뱃길",
        "region": "인천 · 김포 ~ 인천",
        "region_tag": "인천",
        "difficulty": "입문",
        "bike_type": "로드",
        "distance": "26km",
        "duration": "1h 40m",
        "elevation_gain": "120m",
        "rating": 4.5,
        "review_count": 1834,
        "image": "https://images.unsplash.com/photo-1541625602330-2277a4c46182?w=1200&q=70",
        "tags": ["입문", "로드"],
        "station": None,
    },
    {
        "id": "chuncheon-uiamho",
        "name": "춘천 의암호 순환",
        "region": "강원 · 춘천시",
        "region_tag": "강원",
        "difficulty": "중급",
        "bike_type": "그래벨",
        "distance": "35km",
        "duration": "2h 20m",
        "elevation_gain": "420m",
        "rating": 4.8,
        "review_count": 854,
        "image": "https://images.unsplash.com/photo-1767820524140-6b94b57789b5?w=1200&q=70",
        "tags": ["중급", "그래벨"],
        "station": None,
    },
    {
        "id": "jirisan-dulegil",
        "name": "지리산 둘레길 라이딩",
        "region": "전남 · 구례 ~ 하동",
        "region_tag": "전남",
        "difficulty": "고급",
        "bike_type": "그래벨",
        "distance": "110km",
        "duration": "8h 30m",
        "elevation_gain": "2,100m",
        "rating": 4.9,
        "review_count": 421,
        "image": "https://images.unsplash.com/photo-1758998076258-9900be6a51f0?w=1200&q=70",
        "tags": ["고급", "그래벨"],
        "station": None,
    },
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        created, skipped = 0, 0
        for item in ROUTES_SEED:
            if db.get(RouteModel, item["id"]) is not None:
                skipped += 1
                continue

            station = item.pop("station", None)
            route = RouteModel(**{k: v for k, v in item.items() if k != "station"})
            db.add(route)

            if station:
                d_name, d_avail, d_total, a_name, a_avail, a_total = station
                db.add(RouteStationStatusModel(
                    route_id=item["id"],
                    departure_name=d_name,
                    departure_available=d_avail,
                    departure_total=d_total,
                    destination_name=a_name,
                    destination_available=a_avail,
                    destination_total=a_total,
                ))

            created += 1

        db.commit()
        print(f"완료: {created}개 생성, {skipped}개 이미 존재해서 건너뜀")
    finally:
        db.close()


if __name__ == "__main__":
    run()