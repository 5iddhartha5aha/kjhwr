from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import app as data_pipeline

api = FastAPI(title="Wind Forecast Analytics API")
app = api

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@api.get("/api/health")
def health():
    return {"status": "ok"}


@api.get("/api/accuracy")
def get_accuracy():
    try:
        # Retrieve forecast history and actual generation.
        forecasts = data_pipeline.fetch_forecasts(
            "2025-12-31T00:00:00Z",
            "2026-02-01T00:00:00Z",
        )

        actuals = data_pipeline.fetch_actuals(
            "2026-01-01T00:00:00Z",
            "2026-02-02T00:00:00Z",
        )

        # Keep the full history for selecting forecast versions.
        january_start = data_pipeline.pd.Timestamp(
            "2026-01-01T00:00:00Z"
        )
        february_start = data_pipeline.pd.Timestamp(
            "2026-02-01T00:00:00Z"
        )

        forecasts["decision_cutoff"] = (
            forecasts["startTime"].dt.normalize()
            - data_pipeline.pd.Timedelta(days=1)
            + data_pipeline.pd.Timedelta(hours=12)
        )

        eligible = forecasts[
            forecasts["publishTime"] <= forecasts["decision_cutoff"]
        ].copy()

        selected = (
            eligible.sort_values("publishTime")
            .drop_duplicates(subset=["startTime"], keep="last")
        )

        
        selected = selected[
            (selected["startTime"] >= january_start)
            & (selected["startTime"] < february_start)
        ]

        expected_hours = pd.date_range(
            start=january_start,
            end= february_start,
            freq="h",
            inclusive="left",
        )

        actuals = actuals[
            (actuals["startTime"] >= january_start)
            & (actuals["startTime"] < february_start)
        ]

        comparison = data_pipeline.compare_forecasts_with_actuals(
            actuals,
            selected,
        )

        if comparison.empty:
            return {
                "metrics": {},
                "records": [],
                "count": 0,
            }

        error = comparison["error"]

        records = comparison[
            [
                "startTime",
                "publishTime",
                "generation_forecast",
                "generation_actual",
                "error",
                "absolute_error",
            ]
        ].copy()

        records["startTime"] = records["startTime"].astype(str)
        records["publishTime"] = records["publishTime"].astype(str)

        return {
            "metrics": {
                "mae": float(error.abs().mean()),
                "rmse": float((error.pow(2).mean()) ** 0.5),
                "bias": float(error.mean()),
            },
            "count": len(records),
            "records": records.to_dict(orient="records"),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not calculate wind forecast accuracy: {exc}",
        ) from exc
