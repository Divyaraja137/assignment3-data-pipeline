import json
from pathlib import Path

import pandas as pd
import requests


BRONZE_DIR = Path("data/bronze")
BRONZE_DIR.mkdir(parents=True, exist_ok=True)

COUNTRY_CODE = "CA"


def find_existing_gold_file() -> Path:
    gold_path = Path("data/gold/crypto_sentiment_daily.csv")

    if gold_path.exists():
        return gold_path

    raise FileNotFoundError(f"Could not find: {gold_path}")


def get_year_range_from_gold(gold_path: Path) -> list[int]:
    df = pd.read_csv(gold_path)

    if "date" not in df.columns:
        raise ValueError("Gold dataset must contain a 'date' column.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    if df.empty:
        raise ValueError("Gold dataset has no valid dates.")

    min_year = int(df["date"].dt.year.min())
    max_year = int(df["date"].dt.year.max())

    return list(range(min_year, max_year + 1))


def fetch_holidays_for_year(year: int, country_code: str = COUNTRY_CODE) -> list[dict]:
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        raise ValueError(f"Unexpected API response for year {year}: {data}")

    return data


def main():
    gold_path = find_existing_gold_file()
    years = get_year_range_from_gold(gold_path)

    all_holidays = []

    for year in years:
        print(f"Fetching holidays for {year}...")
        records = fetch_holidays_for_year(year)
        all_holidays.extend(records)

        raw_output = BRONZE_DIR / f"holidays_{COUNTRY_CODE}_{year}_raw.json"
        with open(raw_output, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    df = pd.DataFrame(all_holidays)

    combined_output = BRONZE_DIR / f"holidays_{COUNTRY_CODE}_combined_raw.csv"
    df.to_csv(combined_output, index=False)

    print(f"Saved yearly raw JSON files and combined CSV to {BRONZE_DIR}")


if __name__ == "__main__":
    main()