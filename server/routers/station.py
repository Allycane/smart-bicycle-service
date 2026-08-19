import math
import random

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from models.station_model import StationModel

station_router = APIRouter()

# 거리 계산 기준점: 서울시청
SEOUL_CITY_HALL = (37.5665, 126.9780)

# hourlyUsage: 실제 "시간별" 원본 데이터에 시간(0~23시) 컬럼이 있는지 아직 확인 전이라
# 우선 전형적인 출퇴근 러시아워 패턴의 자리표시(placeholder) 값을 사용한다.
# 시간 컬럼 확인되면 이 부분을 실제 집계 쿼리로 교체할 것.
_PLACEHOLDER_HOURLY_SHAPE = [
    1, 1, 1, 1, 1, 2, 4, 10, 20, 13, 8, 8,
    11, 9, 8, 9, 11, 18, 25, 20, 13, 9, 6, 3,
]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """두 좌표 사이의 직선거리(km)를 하버사인 공식으로 계산"""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _format_distance(km: float) -> str:
    meters = km * 1000
    if meters < 1000:
        return f"{int(round(meters))}m"
    return f"{km:.1f}km"


def _status(available: int, total: int) -> str:
    if available <= 0:
        return "EMPTY"
    if total > 0 and available / total <= 0.2:
        return "LOW"
    return "GOOD"


@station_router.get("")
async def get_station_status(
    limit: int = Query(default=6, ge=1, le=50, description="가까운 대여소 중 몇 개를 반환할지"),
    db: Session = Depends(get_db),
) -> dict:
    stations = db.query(StationModel).all()

    scored = []
    for s in stations:
        dist_km = _haversine_km(*SEOUL_CITY_HALL, s.latitude, s.longitude)
        # 실시간 API 연동 전까지 임시로, 거치대수를 넘지 않는 범위의 랜덤값을 "대여 가능 대수"로 사용
        available = random.randint(0, s.rack_count)
        scored.append({
            "id": s.id,
            "name": s.name,
            "distance": _format_distance(dist_km),
            "available": available,
            "total": s.rack_count,
            "status": _status(available, s.rack_count),
            "_dist_km": dist_km,
        })

    scored.sort(key=lambda x: x["_dist_km"])
    nearest = scored[:limit]
    for item in nearest:
        item.pop("_dist_km")

    hourly_usage = [
        {"hour": f"{h}시", "count": v}
        for h, v in enumerate(_PLACEHOLDER_HOURLY_SHAPE)
    ]

    return {
        "stations": nearest,
        "hourlyUsage": hourly_usage,
    }