# Wind Generation Forecast Dashboard

A web-based dashboard for analysing day-ahead UK wind generation forecasts against actual generation. Designed to help energy procurement teams understand forecast accuracy and evaluate historical wind generation patterns.

## Live Application

- **Dashboard:** [https://vercel.app](https://kjhwr-gwo2.vercel.app/)
- **API Documentation:** [https://vercel.appdocs](https://kjhwr-azure.vercel.app/docs)

## Features

- Visualises forecast and actual national wind generation.
- Calculates Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and forecast bias.
- Provides date-range filtering for historical analysis.
- Displays forecast publication timestamps and hourly error records.
- Uses Elexon BMRS data for actual wind generation and wind forecasts.

## Technology Stack

- **Frontend:** React, Recharts, CSS
- **Backend:** Python, FastAPI, Pandas, Requests
- **Data Source:** Elexon BMRS API
- **Containerisation:** Docker and Docker Compose
- **Deployment:** Vercel

## Project Structure

```text
wind-forecast-dashboard/
├── backend/
│   ├── app.py              # Fetches and processes Elexon data
│   ├── main.py             # FastAPI application and API endpoints
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend Docker image configuration
│   └── test_api.py         # API testing and exploration
│
├── frontend/
│   ├── public/             # Static public assets
│   ├── src/
│   │   ├── App.js          # Dashboard components and API integration
│   │   ├── App.css         # Dashboard styling
│   │   └── ...             # Other React source files
│   ├── package.json        # Node.js dependencies and scripts
│   ├── package-lock.json   # Locked dependency versions
│   ├── Dockerfile          # Frontend Docker image configuration
│   └── nginx.conf          # Nginx web server configuration
│
├── docker-compose.yml      # Runs frontend and backend containers
└── README.md               # Project documentation
```

## Data Sources

The dashboard uses the Elexon BMRS API:

- **FUELHH:** Actual electricity generation data. Records are filtered to wind generation.
- **WINDFOR:** Wind generation forecast data, including publication timestamps and forecast values.

API documentation: https://elexon.co.uk

The analysis covers January 2026 and compares hourly forecasts with actual wind generation.

## Running the Application with Docker

### Prerequisites

Install Docker Engine and Docker Compose.

Verify the installation:

```bash
docker --version
docker compose version
```

### Start the application

Clone the repository and navigate to its root directory:

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd wind-forecast-dashboard
```

Build and start the services:

```bash
docker compose up --build -d
```

Open the dashboard:

- Frontend: http://localhost:3000

Check the container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs --tail=50
```

Stop the application:

```bash
docker compose down
```

Docker installs the application dependencies during the image build, so separate system-wide Python or Node.js package installations are not required.

## Running Locally Without Docker

### Backend

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:api --reload
```

The backend API runs at http://127.0.0.1:8000.

API documentation is available at http://127.0.0.

### Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm start
```

The React development server runs at http://localhost:3000.

For local development, the frontend uses `http://127.0.0.1:8000` as its default backend URL. The deployed frontend uses the `REACT_APP_API_URL` environment variable.

## Forecast Accuracy Methodology

For each delivery hour, the latest eligible wind forecast published by 12:00 UTC on the preceding calendar day is selected.

The 12:00 UTC cutoff is a working assumption for this analysis, not a claim about an official market deadline.

The selected forecasts are compared against actual wind generation for January 2026.

The metrics are:

- **MAE:** Mean absolute difference between forecast and actual generation.
- **RMSE:** Root mean squared error, which penalises larger errors more heavily.
- **Bias:** Mean signed forecast error. Positive bias indicates overforecasting; negative bias indicates underforecasting.

All timestamps are displayed in UTC.

## Deployment Configuration

The frontend is deployed on Vercel separately from the FastAPI backend.

The frontend uses the environment variable:

```text
REACT_APP_API_URL=https://vercel.app
```

The backend CORS configuration must allow requests from the deployed frontend domain.

## AI Tools Used

ChatGPT and GitHub Copilot were used to assist with implementation, debugging, code review, Docker configuration, and deployment troubleshooting.

All application code and deployment configurations were reviewed and tested as part of the development process.

---
