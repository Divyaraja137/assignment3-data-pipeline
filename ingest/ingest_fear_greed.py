import requests
import json
import os
from datetime import datetime

url = "https://api.alternative.me/fng/"
params = {
    "limit": 365,
    "format": "json"
}

response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()

os.makedirs("data/bronze/fear_greed", exist_ok=True)

ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
filename = f"data/bronze/fear_greed/fng_{ts}.json"

with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("File saved:", filename)