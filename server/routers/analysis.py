from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.connection import get_db
from models.usage_model import HourlyUsageModel

analysis_router = APIRouter()


def _build_insights(db: Session, monthly_usage: list[dict], top_stations: list[dict], age_distribution: list[dict]) -> list[dict]:
    """
    현재 확보한 컬럼(날짜/시간/대여소/연령대코드/이용건수/이동거리)만으로
    계산 가능한 인사이트 6개. title/description은 InsightCard.jsx 확인 후 필요하면 필드명을 맞춘다.
    """
    insights = []

    # 1. 최다 이용 연령대
    if age_distribution:
        top_age = max(age_distribution, key=lambda x: x["percent"])
        insights.append({
            "title": "핵심 이용 연령대",
            "description": f"연령대코드 '{top_age['age']}' 그룹이 전체 이용의 {top_age['percent']}%를 차지합니다.",
        })

    # 2. 평균 이동 거리
    avg_distance = db.query(func.avg(HourlyUsageModel.distance_m)).scalar()
    if avg_distance:
        insights.append({
            "title": "평균 이동 거리",
            "description": f"1건당 평균 이동 거리는 약 {avg_distance / 1000:.1f}km 입니다.",
        })

    # 3. 계절별 편차 (월별 최고/최저)
    if len(monthly_usage) >= 2:
        best = max(monthly_usage, key=lambda x: x["count"])
        worst = min(monthly_usage, key=lambda x: x["count"])
        if worst["count"] > 0:
            ratio = round(best["count"] / worst["count"], 1)
            insights.append({
                "title": "계절별 이용 편차",
                "description": f"{best['month']}이 이용량이 가장 많고 {worst['month']}이 가장 적어, 최대 {ratio}배 차이가 납니다.",
            })

    # 4. 평일 vs 주말 (MySQL DAYOFWEEK: 1=일 ... 7=토)
    weekday_total = (
        db.query(func.sum(HourlyUsageModel.rental_count))
        .filter(func.dayofweek(HourlyUsageModel.rental_date).notin_([1, 7]))
        .scalar()
    ) or 0
    weekend_total = (
        db.query(func.sum(HourlyUsageModel.rental_count))
        .filter(func.dayofweek(HourlyUsageModel.rental_date).in_([1, 7]))
        .scalar()
    ) or 0
    if weekday_total and weekend_total:
        weekday_avg = weekday_total / 5
        weekend_avg = weekend_total / 2
        diff_pct = round(abs(weekday_avg - weekend_avg) / weekend_avg * 100, 1)
        more = "평일" if weekday_avg > weekend_avg else "주말"
        insights.append({
            "title": "평일 vs 주말",
            "description": f"{more} 일평균 이용량이 더 많아, 평일-주말 간 약 {diff_pct}% 차이가 납니다.",
        })

    # 5. 출퇴근 시간대 비교 (7~9시 vs 18~20시)
    morning_total = (
        db.query(func.sum(HourlyUsageModel.rental_count))
        .filter(HourlyUsageModel.hour.between(7, 9))
        .scalar()
    ) or 0
    evening_total = (
        db.query(func.sum(HourlyUsageModel.rental_count))
        .filter(HourlyUsageModel.hour.between(18, 20))
        .scalar()
    ) or 0
    if morning_total and evening_total:
        higher = "퇴근(18~20시)" if evening_total > morning_total else "출근(7~9시)"
        diff_pct = round(abs(evening_total - morning_total) / min(morning_total, evening_total) * 100, 1)
        insights.append({
            "title": "출퇴근 시간대 비교",
            "description": f"{higher} 시간대의 이용량이 더 많아, 두 시간대 간 약 {diff_pct}% 차이가 납니다.",
        })

    # 6. 최고 인기 대여소
    if top_stations:
        overall_total = db.query(func.sum(HourlyUsageModel.rental_count)).scalar() or 1
        top1 = top_stations[0]
        share = round(top1["count"] / overall_total * 100, 1)
        insights.append({
            "title": "최고 인기 대여소",
            "description": f"'{top1['name']}' 대여소가 전체 이용의 {share}%를 차지하는 1위 대여소입니다.",
        })

    return insights


@analysis_router.get("")
async def get_bike_analysis(db: Session = Depends(get_db)) -> dict:
    # 월별 이용 추이
    monthly_rows = (
        db.query(
            func.date_format(HourlyUsageModel.rental_date, "%Y-%m").label("month"),
            func.sum(HourlyUsageModel.rental_count).label("count"),
        )
        .group_by("month")
        .order_by("month")
        .all()
    )
    monthly_usage = [{"month": r.month, "count": int(r.count)} for r in monthly_rows]

    # 대여소 순위 TOP 6
    top_rows = (
        db.query(
            HourlyUsageModel.station_name.label("name"),
            func.sum(HourlyUsageModel.rental_count).label("count"),
        )
        .group_by(HourlyUsageModel.station_name)
        .order_by(func.sum(HourlyUsageModel.rental_count).desc())
        .limit(6)
        .all()
    )
    top_stations = [{"name": r.name, "count": int(r.count)} for r in top_rows]

    # 연령대별 이용 비율
    age_rows = (
        db.query(
            HourlyUsageModel.age_group.label("age"),
            func.sum(HourlyUsageModel.rental_count).label("count"),
        )
        .group_by(HourlyUsageModel.age_group)
        .all()
    )
    total_age_count = sum(r.count for r in age_rows) or 1
    age_distribution = [
        {"age": r.age, "percent": round(r.count / total_age_count * 100, 1)}
        for r in age_rows
    ]
    age_distribution.sort(key=lambda x: x["age"])

    insights = _build_insights(db, monthly_usage, top_stations, age_distribution)

    return {
        "monthlyUsage": monthly_usage,
        "topStations": top_stations,
        "ageDistribution": age_distribution,
        "insights": insights,
    }