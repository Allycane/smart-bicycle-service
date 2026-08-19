from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class StationModel(Base):
    """
    서울 열린데이터광장 '공공자전거 대여소 정보' 원본 컬럼을 그대로 옮긴 마스터 테이블.
    원본 컬럼: 대여소번호 / 대여소 / 자치구 / 위도 / 경도 / 거치대수
    """
    __tablename__ = "bike_stations"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # 대여소번호
    name: Mapped[str] = mapped_column(String(200), nullable=False)  # 대여소
    district: Mapped[str] = mapped_column(String(50), nullable=False)  # 자치구
    latitude: Mapped[float] = mapped_column(Float, nullable=False)  # 위도
    longitude: Mapped[float] = mapped_column(Float, nullable=False)  # 경도
    rack_count: Mapped[int] = mapped_column(Integer, nullable=False)  # 거치대수