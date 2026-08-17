from sqlalchemy import String, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class MemberStatusModel(Base):
    """
    대시보드에 노출되는 사용자 활동/상태 데이터를 저장하는 테이블.
    bike_member 테이블과는 nickname(PK)을 기준으로 1:1 관계를 가진다.
    """
    __tablename__ = "member_status"

    # bike_member.nickname 을 FK로 참조하는 PK.
    # -> bike_member 이 삭제되면 member_status 도 함께 삭제되도록 CASCADE 설정.
    nickname: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("bike_member.nickname", ondelete="CASCADE"),
        primary_key=True
    )

    # data.user.level
    level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="새싹 라이더"
    )

    # data.user.streak (연속 라이딩 일수)
    streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    # data.activity.badges / challenges / followers / savedRoutes
    badges: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    challenges: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    followers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    saved_routes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # data.totals — StatCard 4개에 그대로 spread 되는 리스트.
    # 예: [{"icon": "Route", "label": "이번 달 주행거리", "value": 0, "unit": "km"}, ...]
    totals: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # data.recommendedRoute
    # 예: {"id": 1, "name": "...", "image": "...", "distance": "...", "duration": "..."}
    recommended_route: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # data.quickMenu
    # 예: [{"label": "루트 탐색", "path": "/routes", "icon": "Map"}, ...]
    quick_menu: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # data.communityFeed
    # 예: [{"initial": "K", "name": "...", "text": "...", "time": "...", "likes": 0}, ...]
    community_feed: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # bike_member <-> member_status 1:1 관계 (조인 편의를 위해 추가)
    member = relationship("MemberModel", backref="status", uselist=False)