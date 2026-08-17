from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from core.security import get_current_user
from models.member_model import MemberModel
from models.dashboard_model import MemberStatusModel
from schemas.dashboard_schemas import DashboardResponse

dashboard_router = APIRouter()


# member_status 행이 아직 없는 신규 회원을 위한 초기값(placeholder).
# quickMenu / recommendedRoute 는 사용자별로 실제 로직이 붙기 전까지는
# 고정값으로 채워둔다 (요청하신 대로).
DEFAULT_TOTALS = [
    {"icon": "Route", "label": "이번 달 주행거리", "value": 0, "unit": "km"},
    {"icon": "Clock", "label": "이번 달 주행시간", "value": 0, "unit": "시간"},
    {"icon": "Flame", "label": "소모 칼로리", "value": 0, "unit": "kcal"},
    {"icon": "TrendingUp", "label": "평균 속도", "value": 0, "unit": "km/h"},
]

DEFAULT_RECOMMENDED_ROUTE = {
    "id": 0,
    "name": "추천 루트가 아직 없어요",
    "image": "/images/routes/placeholder.jpg",
    "distance": "0km",
    "duration": "0분",
}

DEFAULT_QUICK_MENU = [
    {"label": "루트 탐색", "path": "/routes", "icon": "Map"},
    {"label": "챌린지", "path": "/challenges", "icon": "Target"},
    {"label": "커뮤니티", "path": "/community", "icon": "Users"},
    {"label": "내 정보", "path": "/mypage", "icon": "User"},
]

DEFAULT_COMMUNITY_FEED = []


@dashboard_router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    nickname = current_user["nickname"]

    # bike_member 조회 (PK = nickname)
    member = db.get(MemberModel, nickname)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원 정보를 찾을 수 없습니다."
        )

    # member_status 조회, 없으면 최초 접속으로 간주하고 기본값으로 생성
    status_model = db.get(MemberStatusModel, nickname)
    if status_model is None:
        status_model = MemberStatusModel(
            nickname=nickname,
            totals=DEFAULT_TOTALS,
            recommended_route=DEFAULT_RECOMMENDED_ROUTE,
            quick_menu=DEFAULT_QUICK_MENU,
            community_feed=DEFAULT_COMMUNITY_FEED,
        )
        db.add(status_model)
        db.commit()
        db.refresh(status_model)

    # bike_member.created_id 를 기준으로 가입 일수 계산
    # DB에 timezone 정보 없이 저장된 경우(created_id.tzinfo is None) UTC로 간주해서 보정한다.
    created_at = member.created_id
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    joined_days = (datetime.now(timezone.utc) - created_at).days

    return {
        "user": {
            # bike_member 테이블에 별도 "name" 컬럼이 없어 nickname으로 대체함.
            # 추후 실명/표시이름 컬럼이 생기면 이 부분만 교체하면 됨.
            "name": member.nickname,
            "level": status_model.level,
            "handle": f"@{member.nickname}",
            "joinedDays": joined_days,
            "streak": status_model.streak,
        },
        "totals": status_model.totals,
        "recommendedRoute": status_model.recommended_route,
        "activity": {
            "badges": status_model.badges,
            "challenges": status_model.challenges,
            "followers": status_model.followers,
            "savedRoutes": status_model.saved_routes,
        },
        "quickMenu": status_model.quick_menu,
        "communityFeed": status_model.community_feed,
    }