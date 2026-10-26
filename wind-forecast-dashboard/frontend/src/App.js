
import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import "./App.css";

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [startDate, setStartDate] = useState("2026-01-01");
  const [endDate, setEndDate] = useState("2026-01-31");

  useEffect(() => {
    const apiBaseUrl =
      process.env.REACT_APP_API_URL ??
      (process.env.NODE_ENV === "development" ? "http://127.0.0.1:8000" : "");

    fetch(`${apiBaseUrl}/api/accuracy`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch forecast data from the backend.");
        }
        return response.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <div className="container"><h2>Unable to load dashboard</h2><p>{error}</p><p>Check that your Python backend is running.</p></div>;
  }

  if (!data) {
    return <div className="container"><h2>UK Wind Forecast Dashboard</h2><p>Loading forecast data...</p></div>;
  }

  //const metrics = data.metrics || {};
  const filteredRecords = (data.records || []).filter((record) => {
    const deliveryDate = record.startTime.slice(0, 10);
    return deliveryDate >= startDate && deliveryDate <= endDate;
  });

  const chartData = filteredRecords.map((record) => ({
    time: new Date(record.startTime).toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "UTC",
    }),
    forecast: record.generation_forecast,
    actual: record.generation_actual,
  }));

  const latestPublication = filteredRecords.length
  ? filteredRecords.reduce((latest, record) =>
      record.publishTime > latest ? record.publishTime : latest,
      filteredRecords[0].publishTime
    )
  : null;

  const metrics = {
    mae: filteredRecords.length
      ? filteredRecords.reduce((sum, r) => sum + Math.abs(Number(r.error)), 0) /
        filteredRecords.length
      : null,

    rmse: filteredRecords.length
      ? Math.sqrt(
          filteredRecords.reduce((sum, r) => sum + Number(r.error) ** 2, 0) /
            filteredRecords.length
        )
      : null,

    bias: filteredRecords.length
      ? filteredRecords.reduce((sum, r) => sum + Number(r.error), 0) /
        filteredRecords.length
      : null,
  };

  return (
    <main className="container">
      <header className="header">
        <div>
          <p className="eyebrow">ENERGY PROCUREMENT · UNITED KINGDOM</p>
          <h1>Wind Generation Forecast</h1>
          {/* <p className="subtitle">Day-ahead forecast performance · January 2026</p> */}
          <p className="subtitle">
            Day-ahead forecast performance · January 2026
          </p>

          <p className="publication-info">
            Latest selected forecast publication:{" "}
            {latestPublication
              ? new Date(latestPublication).toLocaleString("en-GB", {
                  dateStyle: "medium",
                  timeStyle: "short",
                  timeZone: "UTC",
                }) + " UTC"
              : "No forecast data available"}
          </p>
        </div>
        <span className="status">Historical analysis</span>
      </header>

      <section className="metrics">
        <article className="metric-card">
          <p>Mean Absolute Error</p>
          <h2>{metrics.mae == null ? "—" : metrics.mae.toLocaleString("en-GB", { maximumFractionDigits: 0 })}</h2>
          <span>MW · Lower is better</span>
        </article>
        <article className="metric-card">
          <p>Root Mean Squared Error</p>
          <h2>{metrics.rmse == null ? "—" : metrics.rmse.toLocaleString("en-GB", { maximumFractionDigits: 0 })}</h2>
          <span>MW · Penalises large errors</span>
        </article>
        <article className="metric-card">
          <p>Forecast Bias</p>
          <h2>{metrics.bias == null ? "—" : metrics.bias.toLocaleString("en-GB", { maximumFractionDigits: 0 })}</h2>
          <span>MW · Positive means overforecast</span>
        </article>
        <article className="metric-card">
          <p>Matched Periods</p>
          <h2>{filteredRecords.length.toLocaleString("en-GB")}</h2>
          {/* <h2>{(data.count || 0).toLocaleString("en-GB")}</h2> */}
          <span>Hourly forecast records</span>
        </article>
      </section>

      <section className="panel">
        {/* <div className="panel-heading">
          <div>
            <h2>Forecast vs Actual Generation</h2>
            <p>National wind generation · MW · timestamps in UTC</p>
          </div>
        </div> */}
        <div className="panel-heading">
          <div>
            <h2>Forecast vs Actual Generation</h2>
            <p>National wind generation · MW · timestamps in UTC</p>
          </div>

          <div className="date-filters">
            <label>
              From
              <input
                type="date"
                value={startDate}
                min="2026-01-01"
                max="2026-01-31"
                onChange={(e) => setStartDate(e.target.value)}
              />
            </label>

            <label>
              To
              <input
                type="date"
                value={endDate}
                min={startDate}
                max="2026-01-31"
                onChange={(e) => setEndDate(e.target.value)}
              />
            </label>
          </div>
        </div>
        <div className="chart">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" minTickGap={40} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="forecast" name="Forecast" stroke="#2563eb" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="actual" name="Actual" stroke="#16a34a" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="panel">
        <h2>Forecast Error Records</h2>
        {/* <p className="subtitle">First 50 matched hourly delivery periods</p> */}
        <p className="subtitle">
          Showing {Math.min(filteredRecords.length, 50)} of {filteredRecords.length} matched hourly delivery periods
        </p>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Delivery Time (UTC)</th>
                <th>Published (UTC)</th>
                <th>Forecast (MW)</th>
                <th>Actual (MW)</th>
                <th>Error (MW)</th>
              </tr>
            </thead>
            <tbody>
              {/* {(data.records || []).slice(0, 50).map((record) => ( */}
              {filteredRecords.slice(0, 50).map((record) => (
                <tr key={record.startTime}>
                  <td>{new Date(record.startTime).toLocaleString("en-GB", { timeZone: "UTC" })}</td>
                  <td>{new Date(record.publishTime).toLocaleString("en-GB", { timeZone: "UTC" })}</td>
                  <td>{Number(record.generation_forecast).toLocaleString("en-GB", { maximumFractionDigits: 0 })}</td>
                  <td>{Number(record.generation_actual).toLocaleString("en-GB", { maximumFractionDigits: 0 })}</td>
                  <td className={record.error > 0 ? "positive" : "negative"}>
                    {Number(record.error).toLocaleString("en-GB", { maximumFractionDigits: 0 })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="footer">
        <p>
          Data source: Elexon BMRS · FUELHH (actual generation) and WINDFOR
          (wind forecasts).
        </p>

        <p>
          Methodology: For each delivery hour, the latest forecast published by
          12:00 UTC on the preceding calendar day is selected. Forecast accuracy
          is evaluated against actual wind generation for January 2026.
        </p>

        <p>
          Note: The 12:00 UTC cutoff is a working assumption, not an official
          market deadline. All timestamps are displayed in UTC.
        </p>
      </footer>
    </main>
  );
}

export default App;
