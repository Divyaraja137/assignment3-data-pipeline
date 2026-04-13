from pathlib import Path

import pandas as pd


BRONZE_FILE = Path("data/bronze/holidays_CA_combined_raw.csv")
SILVER_DIR = Path("data/silver")
SILVER_DIR.mkdir(parents=True, exist_ok=True)

SILVER_FILE = SILVER_DIR / "holidays_CA_clean.csv"


def main():
    if not BRONZE_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {BRONZE_FILE}. Run ingest/ingest_holidays.py first."
        )

    df = pd.read_csv(BRONZE_FILE)

    keep_cols = [col for col in [
        "date",
        "localName",
        "name",
        "countryCode",
        "fixed",
        "global",
        "counties",
        "launchYear",
        "types",
    ] if col in df.columns]

    df = df[keep_cols].copy()

    rename_map = {
        "localName": "holiday_local_name",
        "name": "holiday_name",
        "countryCode": "country_code",
        "launchYear": "launch_year",
        "types": "holiday_types",
    }
    df = df.rename(columns=rename_map)

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["holiday_flag"] = 1
    df["day_type"] = "Holiday"

    df = df.sort_values("date").drop_duplicates(subset=["date"], keep="first")

    df.to_csv(SILVER_FILE, index=False)

    print(f"Saved cleaned holiday data to {SILVER_FILE}")


if __name__ == "__main__":
    main()