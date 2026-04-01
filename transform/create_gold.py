import pandas as pd
import os

# read silver files
btc = pd.read_csv("data/silver/btc_daily_clean.csv")
fng = pd.read_csv("data/silver/fear_greed_clean.csv")

# convert date columns to datetime
btc["date"] = pd.to_datetime(btc["date"])
fng["date"] = pd.to_datetime(fng["date"])

# join both datasets on date
gold = pd.merge(btc, fng, on="date", how="inner")

# sort by date
gold = gold.sort_values("date")

# create new columns
gold["btc_daily_return"] = gold["btc_close"].pct_change()
gold["positive_return"] = (gold["btc_daily_return"] > 0).astype(int)
gold["is_weekend"] = gold["date"].dt.dayofweek.isin([5, 6]).astype(int)

# remove first row with null return
gold = gold.dropna()

# create gold folder if needed
os.makedirs("data/gold", exist_ok=True)

# save final gold dataset
gold.to_csv("data/gold/crypto_sentiment_daily.csv", index=False)

print("Saved: data/gold/crypto_sentiment_daily.csv")
print(gold.head())
print(gold.columns)