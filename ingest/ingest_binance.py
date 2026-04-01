import requests
import json
import os
from datetime import datetime

# API endpoint
url = "https://api.binance.com/api/v3/klines"

params = {
    "symbol": "BTCUSDT",
    "interval": "1d",
    "limit": 365
}

# API call
response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()

# create folder if not exists
os.makedirs("data/bronze/binance", exist_ok=True)

# timestamp file name
ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

filename = f"data/bronze/binance/btc_klines_{ts}.json"

# save file
with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("File saved:", filename)