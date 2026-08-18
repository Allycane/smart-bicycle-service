from sqlalchemy import String, Integer, Float, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class RouteModel(Base):
    """
    개인 라이딩 루트와 따릉이 루트를 하나의 테이블에서 관리한다.
    bike_type 값으로 구분: "따릉이" 는 공유 자전거, 그 외(MTB/로드/그래벨/투어링/도심 등)는 개인 라이딩 루트.
    """
    __tablename__ = "routes"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    region: Mapped[str] = mapped_column(String(200), nullable=False)
    region_tag: Mapped[str | None] = mapped_column(String(50), nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bike_type: Mapped[str] = mapped_column(String(50), nullable=False)

    distance: Mapped[str] = mapped_column(String(50), nullable=False)
    duration: Mapped[str] = mapped_column(String(50), nullable=False)

    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    image: Mapped[str] = mapped_column(String(500), nullable=False)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    free: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)

    elevation_gain: Mapped[str | None] = mapped_column(String(50), nullable=True)
    max_elevation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    completion_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    season: Mapped[str | None] = mapped_column(String(50), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    safety_tips: Mapped[list | None] = mapped_column(JSON, nullable=True)
    elevation_profile: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # 따릉이 루트에만 존재하는 출발/도착 대여소 현황 (1:1)
    station_status: Mapped["RouteStationStatusModel"] = relationship(
        "RouteStationStatusModel",
        uselist=False,
        backref="route",
        cascade="all, delete-orphan"
    )


class RouteStationStatusModel(Base):
    """
    따릉이 루트의 출발/도착 대여소 실시간(현재는 목업) 현황.
    routes 테이블과 정적/동적 데이터를 분리해서, 추후 실제 공공 API로
    이 테이블만 주기적으로 갱신하는 구조로 확장하기 위해 별도 테이블로 둔다.
    """
    __tablename__ = "route_station_status"

    route_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("routes.id", ondelete="CASCADE"),
        primary_key=True
    )

    departure_name: Mapped[str] = mapped_column(String(200), nullable=False)
    departure_available: Mapped[int] = mapped_column(Integer, nullable=False)
    departure_total: Mapped[int] = mapped_column(Integer, nullable=False)

    destination_name: Mapped[str] = mapped_column(String(200), nullable=False)
    destination_available: Mapped[int] = mapped_column(Integer, nullable=False)
    destination_total: Mapped[int] = mapped_column(Integer, nullable=False)