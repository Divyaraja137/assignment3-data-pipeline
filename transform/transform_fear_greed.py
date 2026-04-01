import json
import pandas as pd
import glob
import os

# find latest bronze file
files = glob.glob("data/bronze/fear_greed/*.json")
latest_file = max(files, key=os.path.getctime)

# open json file
with open(latest_file, "r", encoding="utf-8") as f:
    raw = json.load(f)

# convert json data to dataframe
df = pd.DataFrame(raw["data"])

# clean columns
df["timestamp"] = df["timestamp"].astype(int)
df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
df["fear_greed_value"] = df["value"].astype(int)
df["fear_greed_label"] = df["value_classification"]

# keep needed columns
silver = df[["date", "fear_greed_value", "fear_greed_label"]]

# save csv
os.makedirs("data/silver", exist_ok=True)
silver.to_csv("data/silver/fear_greed_clean.csv", index=False)

print("Saved: data/silver/fear_greed_clean.csv")
print(silver.head())