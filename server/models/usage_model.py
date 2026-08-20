from datetime import date

from sqlalchemy import String, Integer, Float, Date
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class HourlyUsageModel(Base):
    """
    시간별 공공자전거 이용 데이터.
    원본 컬럼: 대여일자 / 대여시간 / 대여소번호 / 대여소 / 연령대 / 이동거리(M) / 이용시간(분) / 이용건수
    한 행 = (날짜, 시간, 대여소, 연령대) 조합별 집계 건수.
    """
    __tablename__ = "bike_hourly_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rental_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hour: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # 0~23
    station_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    station_name: Mapped[str] = mapped_column(String(200), nullable=False)
    age_group: Mapped[str] = mapped_column(String(20), nullable=False)
    distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    rental_count: Mapped[int] = mapped_column(Integer, nullable=False)


class DailyUsageModel(Base):
    """
    일별 공공자전거 이용 데이터.
    원본 컬럼: 대여일자 / 대여소번호 / 대여소 / 연령대 / 이용시간(분) / 이동거리(M) / 이용건수
    """
    __tablename__ = "bike_daily_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rental_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    station_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    station_name: Mapped[str] = mapped_column(String(200), nullable=False)
    age_group: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    rental_count: Mapped[int] = mapped_column(Integer, nullable=False)


class MonthlyUsageModel(Base):
    """
    월별 공공자전거 이용 데이터.
    원본 컬럼: 자치구 / 기준년월 / 대여건수 / 반납건수 / 대여소번호 / 대여소
    """
    __tablename__ = "bike_monthly_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    district: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    year_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)  # "2026-01"
    rental_count: Mapped[int] = mapped_column(Integer, nullable=False)
    return_count: Mapped[int] = mapped_column(Integer, nullable=False)
    station_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    station_name: Mapped[str] = mapped_column(String(200), nullable=False)