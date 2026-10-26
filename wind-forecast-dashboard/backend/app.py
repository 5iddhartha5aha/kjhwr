import requests
import pandas as pd

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"


def fetch_data(dataset, params):
    url = f"{BASE_URL}/{dataset}/stream"

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return pd.DataFrame(response.json())


def fetch_forecasts(publish_from, publish_to):
    params = {
        "publishDateTimeFrom": publish_from,
        "publishDateTimeTo": publish_to,
    }

    df = fetch_data("WINDFOR", params)

    df["publishTime"] = pd.to_datetime(df["publishTime"], utc=True)
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    return df


def fetch_actuals(publish_from, publish_to):
    params = {
        "publishDateTimeFrom": publish_from,
        "publishDateTimeTo": publish_to,
    }

    df = fetch_data("FUELHH", params)

    df = df[df["fuelType"] == "WIND"].copy()

    df["publishTime"] = pd.to_datetime(df["publishTime"], utc=True)
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)

    return df[["startTime", "generation"]]



def select_forecast_versions(forecasts, decision_cutoff):
    cutoff = pd.Timestamp(decision_cutoff)

    if cutoff.tzinfo is None:
        cutoff = cutoff.tz_localize("UTC")
    else:
        cutoff = cutoff.tz_convert("UTC")

    # Only forecasts published by the decision cutoff
    eligible = forecasts[
        forecasts["publishTime"] <= cutoff
    ].copy()

    # Only delivery periods after the decision cutoff
    eligible = eligible[
        eligible["startTime"] > cutoff
    ]

    # Select the latest eligible forecast for each delivery period
    selected = (
        eligible.sort_values("publishTime")
        .drop_duplicates(subset=["startTime"], keep="last")
    )

    return selected

def calculate_accuracy(actuals, forecasts):
    merged = actuals.merge(
        forecasts[["startTime", "generation"]],
        on="startTime",
        how="inner",
        suffixes=("_actual", "_forecast"),
    )

    merged = merged.dropna(
        subset=["generation_actual", "generation_forecast"]
    )

    if merged.empty:
        return merged, {}

    error = (
        merged["generation_forecast"]
        - merged["generation_actual"]
    )

    metrics = {
        "MAE": error.abs().mean(),
        "RMSE": (error.pow(2).mean()) ** 0.5,
        "Bias": error.mean(),
    }

    merged["error"] = error
    merged["absolute_error"] = error.abs()

    return merged, metrics


def compare_forecasts_with_actuals(actuals, selected_forecasts):
    # Keep only delivery periods available in both datasets
    merged = actuals.merge(
        selected_forecasts[
            ["startTime", "generation", "publishTime"]
        ],
        on="startTime",
        how="inner",
        suffixes=("_actual", "_forecast"),
    )

    merged = merged.dropna(
        subset=["generation_actual", "generation_forecast"]
    )

    if merged.empty:
        print("No matching actual and forecast records found.")
        return merged

    merged["error"] = (
        merged["generation_forecast"]
        - merged["generation_actual"]
    )

    merged["absolute_error"] = merged["error"].abs()

    print("Matching delivery periods:", len(merged))
    print("\nSample comparisons:")
    print(
        merged[
            [
                "startTime",
                "publishTime",
                "generation_forecast",
                "generation_actual",
                "error",
            ]
        ].head(10).to_string(index=False)
    )

    print("\nAccuracy metrics:")
    print("MAE:", merged["absolute_error"].mean())
    print("RMSE:", (merged["error"].pow(2).mean()) ** 0.5)
    print("Bias:", merged["error"].mean())

    return merged

if __name__ == "__main__":
    # Load forecast history covering the January delivery period.
    forecasts = fetch_forecasts(
        "2025-12-31T00:00:00Z",
        "2026-02-01T00:00:00Z",
    )

    # Load actual generation for January delivery periods.
    actuals = fetch_actuals(
        "2026-01-01T00:00:00Z",
        "2026-02-02T00:00:00Z",
    )

    # Keep January delivery periods only.
    january_start = pd.Timestamp("2026-01-01T00:00:00Z")
    february_start = pd.Timestamp("2026-02-01T00:00:00Z")

    forecasts = forecasts[
        (forecasts["startTime"] >= january_start)
        & (forecasts["startTime"] < february_start)
    ].copy()

    actuals = actuals[
        (actuals["startTime"] >= january_start)
        & (actuals["startTime"] < february_start)
    ].copy()

    # Example decision cutoff: noon UTC on the previous day.
    # This is a testing assumption, not a verified market deadline.
    forecasts["decision_date"] = (
        forecasts["startTime"].dt.normalize()
        - pd.Timedelta(days=1)
    )

    forecasts["decision_cutoff"] = (
        forecasts["decision_date"]
        + pd.Timedelta(hours=12)
    )

    eligible = forecasts[
        forecasts["publishTime"] <= forecasts["decision_cutoff"]
    ].copy()

    selected = (
        eligible.sort_values("publishTime")
        .drop_duplicates(subset=["startTime"], keep="last")
    )

    comparison = compare_forecasts_with_actuals(
        actuals,
        selected,
    )

    if not comparison.empty:
        print("\nJanuary evaluation summary")
        print("Delivery periods evaluated:", len(comparison))
        print("MAE:", comparison["absolute_error"].mean())
        print("RMSE:", (comparison["error"].pow(2).mean()) ** 0.5)
        print("Bias:", comparison["error"].mean())
