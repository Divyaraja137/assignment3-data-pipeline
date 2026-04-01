# Assignment 3 - Data Pipeline for Statistical Analysis

## Project Overview
This project uses Pack A: Crypto & Sentiment.

The pipeline collects Bitcoin daily market data from Binance and Fear & Greed sentiment data from Alternative.me.
The raw API data is stored in the Bronze layer, cleaned data is stored in the Silver layer, and the final joined dataset is stored in the Gold layer.

## APIs Used
1. Binance Market Data API
2. Alternative.me Fear & Greed Index API

## Folder Structure
- `data/bronze/` = raw API snapshots
- `data/silver/` = cleaned data tables
- `data/gold/` = final joined analysis-ready dataset

## How to Run

### Bronze
- `python ingest\ingest_binance.py`
- `python ingest\ingest_fear_greed.py`

### Silver
- `python transform\transform_binance.py`
- `python transform\transform_fear_greed.py`

### Gold
- `python transform\create_gold.py`

## Gold Dataset Columns
- `date`
- `btc_open`
- `btc_high`
- `btc_low`
- `btc_close`
- `btc_volume`
- `fear_greed_value`
- `fear_greed_label`
- `btc_daily_return`
- `positive_return`
- `is_weekend`

## Statistical Analysis Plan
This dataset is designed for Part 2 statistical analysis.
One possible question is whether Bitcoin daily returns differ between Fear days and Greed days.

## AI Usage
I used ChatGPT to help with starter code, JSON parsing, debugging, and data transformation.
I checked the date formatting and verified that both datasets joined correctly on the date column.
One issue I had to fix myself was converting the Fear & Greed timestamp into integer format before converting it into a date.