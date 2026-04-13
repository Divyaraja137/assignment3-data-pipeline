from pathlib import Path

import numpy as np
import pandas as pd


SILVER_HOLIDAYS = Path("data/silver/holidays_CA_clean.csv")
GOLD_DIR = Path("data/gold")
GOLD_DIR.mkdir(parents=True, exist_ok=True)

FINAL_GOLD_FILE = GOLD_DIR / "final_assignment4_dataset.csv"


def find_existing_gold_file() -> Path:
    gold_path = Path("data/gold/crypto_sentiment_daily.csv")

    if gold_path.exists():
        return gold_path

    raise FileNotFoundError(f"Could not find: {gold_path}")


def main():
    base_gold_path = find_existing_gold_file()

    if not SILVER_HOLIDAYS.exists():
        raise FileNotFoundError(
            f"Could not find {SILVER_HOLIDAYS}. Run transform/transform_holidays.py first."
        )

    gold_df = pd.read_csv(base_gold_path)
    holidays_df = pd.read_csv(SILVER_HOLIDAYS)

    if "date" not in gold_df.columns:
        raise ValueError("Base Gold dataset must contain 'date' column.")

    gold_df["date"] = pd.to_datetime(gold_df["date"], errors="coerce").dt.date
    holidays_df["date"] = pd.to_datetime(holidays_df["date"], errors="coerce").dt.date

    merged = pd.merge(gold_df, holidays_df, on="date", how="left")

    merged["holiday_flag"] = merged["holiday_flag"].fillna(0).astype(int)
    merged["day_type"] = np.where(merged["holiday_flag"] == 1, "Holiday", "Non-Holiday")

    if "holiday_name" in merged.columns:
        merged["holiday_name"] = merged["holiday_name"].fillna("Not a holiday")
    if "holiday_local_name" in merged.columns:
        merged["holiday_local_name"] = merged["holiday_local_name"].fillna("Not a holiday")
    if "country_code" in merged.columns:
        merged["country_code"] = merged["country_code"].fillna("CA")

    if "btc_daily_return" in merged.columns:
        merged["return_category"] = np.where(
            merged["btc_daily_return"] > 0,
            "Positive",
            np.where(merged["btc_daily_return"] < 0, "Negative", "Flat")
        )

        merged["high_volatility_flag"] = np.where(
            merged["btc_daily_return"].abs() > merged["btc_daily_return"].abs().median(),
            1,
            0
        )

    if "fear_greed_value" in merged.columns:
        merged["fear_greed_group"] = pd.cut(
            merged["fear_greed_value"],
            bins=[-np.inf, 24, 49, 74, np.inf],
            labels=["Extreme Fear", "Fear/Neutral", "Greed", "Extreme Greed"]
        )

    merged["date"] = pd.to_datetime(merged["date"], errors="coerce")
    merged["year"] = merged["date"].dt.year
    merged["month"] = merged["date"].dt.month
    merged["month_name"] = merged["date"].dt.month_name()
    merged["day_name"] = merged["date"].dt.day_name()
    merged["date"] = merged["date"].dt.strftime("%Y-%m-%d")

    merged.to_csv(FINAL_GOLD_FILE, index=False)

    print(f"Saved Assignment 4 Gold dataset to {FINAL_GOLD_FILE}")


if __name__ == "__main__":
    main()