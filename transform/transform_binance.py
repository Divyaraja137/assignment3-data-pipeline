import json
import pandas as pd
import glob
import os

# find latest bronze file
files = glob.glob("data/bronze/binance/*.json")
latest_file = max(files, key=os.path.getctime)

# open json file
with open(latest_file, "r", encoding="utf-8") as f:
    raw = json.load(f)

# create dataframe
df = pd.DataFrame(raw, columns=[
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "num_trades",
    "taker_buy_base", "taker_buy_quote", "ignore"
])

# clean columns
df["date"] = pd.to_datetime(df["open_time"], unit="ms").dt.date
df["btc_open"] = df["open"].astype(float)
df["btc_high"] = df["high"].astype(float)
df["btc_low"] = df["low"].astype(float)
df["btc_close"] = df["close"].astype(float)
df["btc_volume"] = df["volume"].astype(float)

# keep useful columns only
silver = df[["date", "btc_open", "btc_high", "btc_low", "btc_close", "btc_volume"]]

# save silver csv
os.makedirs("data/silver", exist_ok=True)
silver.to_csv("data/silver/btc_daily_clean.csv", index=False)

print("Saved: data/silver/btc_daily_clean.csv")
print(silver.head())