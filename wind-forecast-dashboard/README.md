# Wind Forecast Dashboard

## Run with Docker

Install and start Docker Desktop, then run these commands from the project root:

```sh
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000). The frontend is served by
Nginx, which forwards `/api` requests to the FastAPI backend. To stop the
containers, press `Ctrl+C`; run `docker compose down` to remove them.

The backend fetches forecast and actual-generation data from the Elexon BMRS
API at runtime, so the containers need outbound internet access.
