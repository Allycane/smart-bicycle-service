import glob
import os
import sys

import pandas as pd

from database.connection import engine, Base
from models.usage_model import HourlyUsageModel, DailyUsageModel, MonthlyUsageModel

TABLE_CONFIG = {
    "hourly": {
        "table": "bike_hourly_usage",
        # 연도/월/일은 별도로 date_parts에서 처리하므로 rename에는 넣지 않는다.
        "date_parts": {"year": "연도", "month": "월", "day": "일"},
        "rename": {
            "대여시간": "hour",
            "대여소번호": "station_id",
            "대여소": "station_name",
            "연령대코드": "age_group",
            "이동거리(M)": "distance_m",
            "이용건수": "rental_count",
        },
        "required": ["rental_date", "hour", "station_id", "rental_count"],
    },
    "daily": {
        "table": "bike_daily_usage",
        "date_parts": None,
        "rename": {
            "대여일자": "rental_date",
            "대여소번호": "station_id",
            "대여소": "station_name",
            "연령대": "age_group",
            "이용시간(분)": "duration_min",
            "이동거리(M)": "distance_m",
            "이용건수": "rental_count",
        },
        "date_cols": ["rental_date"],
        "required": ["rental_date", "station_id", "rental_count"],
    },
    "monthly": {
        "table": "bike_monthly_usage",
        "date_parts": None,
        "rename": {
            "자치구": "district",
            "기준년월": "year_month",
            "대여건수": "rental_count",
            "반납건수": "return_count",
            "대여소번호": "station_id",
            "대여소": "station_name",
        },
        "date_cols": [],
        "required": ["district", "year_month", "station_id", "rental_count"],
    },
}


def _resolve_csv_paths(path: str) -> list[str]:
    if os.path.isdir(path):
        paths = sorted(glob.glob(os.path.join(path, "*.csv")))
        if not paths:
            print(f"폴더 안에 csv 파일이 없습니다: {path}")
            sys.exit(1)
        return paths
    return [path]


def _load_one_file(kind: str, config: dict, csv_path: str) -> tuple[int, int]:
    try:
        df = pd.read_csv(csv_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")

    required_source_cols = list(config["rename"].keys())
    if config.get("date_parts"):
        required_source_cols += list(config["date_parts"].values())

    missing = [c for c in required_source_cols if c not in df.columns]
    if missing:
        print(f"[{os.path.basename(csv_path)}] CSV에 다음 컬럼이 없습니다: {missing}")
        print(f"실제 컬럼: {list(df.columns)}")
        sys.exit(1)

    # 연도/월/일 3개 컬럼을 하나의 날짜로 결합 (hourly)
    if config.get("date_parts"):
        dp = config["date_parts"]
        date_parts_df = df[[dp["year"], dp["month"], dp["day"]]].rename(
            columns={dp["year"]: "year", dp["month"]: "month", dp["day"]: "day"}
        )
        df["rental_date"] = pd.to_datetime(date_parts_df, errors="coerce").dt.date

    df = df.rename(columns=config["rename"])

    keep_cols = list(config["rename"].values())
    if "rental_date" in df.columns and "rental_date" not in keep_cols:
        keep_cols = ["rental_date"] + keep_cols
    df = df[keep_cols]

    # daily/monthly 처럼 단일 날짜 컬럼을 그대로 파싱해야 하는 경우
    for col in config.get("date_cols", []):
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    if kind == "monthly":
        df["year_month"] = (
            df["year_month"].astype(str).str.replace("-", "", regex=False).str[:6]
        )
        df["year_month"] = df["year_month"].str[:4] + "-" + df["year_month"].str[4:6]

    before = len(df)
    df = df.dropna(subset=config["required"])
    dropped = before - len(df)

    if kind == "hourly":
        df["hour"] = df["hour"].astype(int)
        df["age_group"] = df["age_group"].astype(str)

    df.to_sql(
        config["table"],
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )

    return len(df), dropped


def run(kind: str, path: str):
    if kind not in TABLE_CONFIG:
        print(f"kind는 hourly / daily / monthly 중 하나여야 합니다: {kind}")
        sys.exit(1)

    config = TABLE_CONFIG[kind]

    _ = (HourlyUsageModel, DailyUsageModel, MonthlyUsageModel)
    Base.metadata.create_all(bind=engine)

    csv_paths = _resolve_csv_paths(path)
    print(f"대상 파일 {len(csv_paths)}개")

    total_loaded, total_dropped = 0, 0
    for i, csv_path in enumerate(csv_paths, 1):
        print(f"[{i}/{len(csv_paths)}] {os.path.basename(csv_path)} 적재 중...")
        loaded, dropped = _load_one_file(kind, config, csv_path)
        total_loaded += loaded
        total_dropped += dropped
        print(f"  -> {loaded:,}행 적재 ({dropped:,}행 제외)")

    print(f"\n전체 완료: {total_loaded:,}행 적재, {total_dropped:,}행 제외 (파일 {len(csv_paths)}개)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python load_usage_data.py <hourly|daily|monthly> <csv_경로 또는 폴더_경로>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])