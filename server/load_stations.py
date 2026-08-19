"""
서울 열린데이터광장 '공공자전거 대여소 정보' CSV를 bike_stations 테이블로 적재하는 스크립트.

전제: CSV에 다음 컬럼이 있어야 함 (말씀해주신 컬럼 목록 기준)
    대여소번호 / 대여소 / 자치구 / 위도 / 경도 / 거치대수

사용법 (프로젝트 루트에서):
    pip install pandas --break-system-packages   # 아직 없다면
    python load_stations.py path/to/대여소_정리본.csv

기존에 같은 대여소번호가 있으면 값만 갱신하고, 없으면 새로 추가합니다.
(여러 번 실행해도 안전 — 데이터 최신화 시 그냥 다시 실행하면 됩니다.)
"""

import sys

import pandas as pd

from database.connection import SessionLocal, engine, Base
from models.station_model import StationModel

REQUIRED_COLUMNS = ["대여소번호", "대여소", "자치구", "위도", "경도", "거치대수"]


def run(csv_path: str):
    Base.metadata.create_all(bind=engine)

    # 서울 열린데이터광장 CSV는 보통 cp949(EUC-KR) 인코딩인 경우가 많아 우선 그걸 시도하고,
    # 실패하면 utf-8-sig(엑셀에서 다시 저장한 경우 흔함)로 재시도한다.
    try:
        df = pd.read_csv(csv_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print(f"CSV에 다음 컬럼이 없습니다: {missing}")
        print(f"실제 컬럼: {list(df.columns)}")
        sys.exit(1)

    db = SessionLocal()
    try:
        created, updated, skipped = 0, 0, 0

        for _, row in df.iterrows():
            try:
                station_id = str(row["대여소번호"]).strip()
                name = str(row["대여소"]).strip()
                district = str(row["자치구"]).strip()
                latitude = float(row["위도"])
                longitude = float(row["경도"])
                rack_count = int(row["거치대수"])
            except (ValueError, TypeError):
                skipped += 1
                continue

            existing = db.get(StationModel, station_id)
            if existing:
                existing.name = name
                existing.district = district
                existing.latitude = latitude
                existing.longitude = longitude
                existing.rack_count = rack_count
                updated += 1
            else:
                db.add(StationModel(
                    id=station_id,
                    name=name,
                    district=district,
                    latitude=latitude,
                    longitude=longitude,
                    rack_count=rack_count,
                ))
                created += 1

        db.commit()
        print(f"완료: {created}개 생성, {updated}개 갱신, {skipped}개 값 이상으로 건너뜀")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python load_stations.py <csv_경로>")
        sys.exit(1)
    run(sys.argv[1])