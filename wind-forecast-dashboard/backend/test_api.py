import requests
import pandas as pd

URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream"

params = {
    "publishDateTimeFrom": "2026-01-01T00:00:00Z",
    "publishDateTimeTo": "2026-01-02T00:00:00Z",
}

response = requests.get(URL, params=params, timeout=30)
response.raise_for_status()

df = pd.DataFrame(response.json())

# Parse timestamps as timezone-aware datetimes
df["publishTime"] = pd.to_datetime(df["publishTime"], utc=True)
df["startTime"] = pd.to_datetime(df["startTime"], utc=True)

print("Publication range:")
print(df["publishTime"].min(), "to", df["publishTime"].max())

print("\nDelivery range:")
print(df["startTime"].min(), "to", df["startTime"].max())

# Check whether generation differs across publication versions
variation = (
    df.groupby("startTime")["generation"]
    .agg(["count", "nunique", "min", "max"])
)

print("\nForecast variation across versions:")
print(variation.head(15).to_string())

print(
    "\nDelivery periods with changing forecasts:",
    (variation["nunique"] > 1).sum()
)

# Check coverage by publication date
df["publication_date"] = df["publishTime"].dt.date

print("\nRecords per publication date:")
print(df.groupby("publication_date").size())
