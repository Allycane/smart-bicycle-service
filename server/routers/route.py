from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.connection import get_db
from models.routes_model import RouteModel
from schemas.routes_schema import RouteOut

route_router = APIRouter()


def _serialize_route(route: RouteModel) -> dict:
    """RouteModel(+ 연결된 station_status)을 프론트가 기대하는 camelCase 딕셔너리로 변환"""
    departure = None
    destination = None

    if route.station_status is not None:
        s = route.station_status
        departure = {
            "name": s.departure_name,
            "available": s.departure_available,
            "total": s.departure_total,
        }
        destination = {
            "name": s.destination_name,
            "available": s.destination_available,
            "total": s.destination_total,
        }

    return {
        "id": route.id,
        "name": route.name,
        "region": route.region,
        "regionTag": route.region_tag,
        "difficulty": route.difficulty,
        "bikeType": route.bike_type,
        "distance": route.distance,
        "duration": route.duration,
        "rating": route.rating,
        "reviewCount": route.review_count,
        "image": route.image,
        "tags": route.tags or [],
        "free": route.free,
        "departure": departure,
        "destination": destination,
        "elevationGain": route.elevation_gain,
        "maxElevation": route.max_elevation,
        "completionRate": route.completion_rate,
        "participants": route.participants,
        "season": route.season,
        "description": route.description,
        "safetyTips": route.safety_tips,
        "elevationProfile": route.elevation_profile,
    }


@route_router.get("", response_model=list[RouteOut])
async def list_routes(
    type: Optional[str] = Query(
        default=None,
        description="'personal' 이면 따릉이(bike_type='따릉이')를 제외한 개인 라이딩 루트만 반환"
    ),
    bikeType: Optional[str] = Query(
        default=None,
        description="특정 bike_type 값으로 필터링 (예: 따릉이, MTB, 로드, 그래벨 등)"
    ),
    db: Session = Depends(get_db),
) -> list[dict]:
    query = db.query(RouteModel)

    if type == "personal":
        query = query.filter(RouteModel.bike_type != "따릉이")

    if bikeType:
        query = query.filter(RouteModel.bike_type == bikeType)

    routes = query.all()
    return [_serialize_route(r) for r in routes]


@route_router.get("/{route_id}", response_model=RouteOut)
async def get_route_detail(route_id: str, db: Session = Depends(get_db)) -> dict:
    route = db.get(RouteModel, route_id)

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 루트를 찾을 수 없습니다."
        )

    return _serialize_route(route)