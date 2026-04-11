# Predictive Engineering Intelligence Platform

![Predictive Engineering Intelligence Platform](assets/images/pasted-image-2.png)

Predictive Engineering Intelligence is a full-stack analytics application with:

- FastAPI backend for data ingestion, scoring, forecasting, and report APIs
- Next.js frontend for dashboard-driven exploration and executive views

The repository is configured for local development and container-based deployment (Render).

## Architecture

## System Architecture

### Logical View

```mermaid
flowchart LR
		U[User Browser] --> FE[Frontend - Next.js App Router\nPort 3000]
		FE --> API[Backend - FastAPI\nPort 10000]

		API --> ROUTES[API Routes Layer\nhealth, runs, repositories, lineage,\nhealth_scores, risk_forecasts, executive_reports]
		ROUTES --> DOMAIN[Domain and Service Layer\nScoring, forecasting, report orchestration]
		DOMAIN --> INFRA[Infrastructure Layer\nDB init, persistence, external tooling]

		INFRA --> DATA[(Local Data Store\nbackend/data)]
		API --> HEALTH[/health and /healthz]

		subgraph Deploy
			FE
			API
		end
```

### Layered Breakdown

- Presentation layer:
	- Next.js UI pages and navigation shell in `frontend/app` and `frontend/components`.
	- Handles user interaction, route transitions, and API consumption.
- API layer:
	- FastAPI routers in `backend/app/api/routes` expose domain capabilities as HTTP contracts.
	- Centralized middleware covers CORS and request identity propagation.
- Domain layer:
	- Business logic under `backend/app/domain` computes engineering health, risk, and reporting outputs.
- Infrastructure layer:
	- `backend/app/infra` initializes storage and wiring.
	- Data artifacts are persisted in `backend/data`.

### Runtime Interaction

1. Browser requests dashboard/report pages from Next.js.
2. Frontend calls FastAPI endpoints using configured `NEXT_PUBLIC_API_BASE_URL`.
3. Backend routes validate input and invoke domain logic.
4. Domain logic reads/writes through infrastructure services and local data store.
5. API returns structured JSON; frontend renders insights and report views.

### High-Level Flow

1. Frontend (Next.js) calls backend API endpoints.
2. Backend (FastAPI) initializes persistence on startup and serves domain routes.
3. Backend computes metrics/insights and returns structured responses.
4. Frontend renders dashboards and report views from backend data.

### Main Components

- Frontend: `frontend/`
	- App Router pages: `frontend/app/`
	- Shared UI shell: `frontend/components/layout/app-shell.tsx`
	- Styles: `frontend/styles/`
- Backend: `backend/`
	- FastAPI entrypoint: `backend/app/main.py`
	- API routes: `backend/app/api/routes/`
		- `health.py`
		- `health_scores.py`
		- `lineage.py`
		- `executive_reports.py`
		- `repositories.py`
		- `risk_forecasts.py`
		- `runs.py`
	- Tests: `backend/tests/`

### Runtime Ports

- Frontend: `3000`
- Backend: `10000`

## Prerequisites

- Node.js 20+
- npm 9+
- Python 3.12+ (3.14 also works in this repo)
- Optional: Docker (for containerized runs)

## Local Setup

### 1) Clone and install frontend dependencies

```powershell
git clone https://github.com/Abhiman1206/obsidian-prism.git
cd obsidian-prism
npm --prefix frontend install
```

### 2) Create/activate Python environment for backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies (mirrors `backend/Dockerfile`):

```powershell
python -m pip install --upgrade pip
pip install fastapi "uvicorn[standard]" pydantic httpx cryptography radon langchain-core langchain-groq pydriller reportlab pytest
```

### 3) Environment configuration

Backend optional variables:

- `ALLOWED_ORIGINS` (comma-separated CORS origins)
- `APP_ENV` (`development` by default)
- `PORT` (defaults to `10000` in containerized backend)

Frontend required for API integration:

- `NEXT_PUBLIC_API_BASE_URL` (example: `http://localhost:10000`)

You can set frontend env in `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:10000
```

## Execution Steps

### Start Backend (Terminal 1)

```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 10000
```

### Start Frontend (Terminal 2)

```powershell
cd frontend
npm run dev -- --hostname 0.0.0.0 --port 3000
```

Open:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:10000/healthz`

## Validation and Quality Checks

### Backend tests

```powershell
$env:PYTHONPATH="backend"
pytest backend/tests -q
```

### Frontend type checks

```powershell
npm --prefix frontend run typecheck
```

### Frontend build

```powershell
npm --prefix frontend run build
```

## Container Build

Build images:

```powershell
docker build -f backend/Dockerfile backend
docker build -f frontend/Dockerfile frontend
```

Run backend container:

```powershell
docker run --rm -p 10000:10000 -e PORT=10000 <backend-image-id>
```

Run frontend container:

```powershell
docker run --rm -p 3000:3000 -e PORT=3000 -e NEXT_PUBLIC_API_BASE_URL=http://host.docker.internal:10000 <frontend-image-id>
```

## Deployment (Render)

`render.yaml` defines two web services:

- `pei-backend`
	- Dockerfile: `backend/Dockerfile`
	- Health check: `/healthz`
	- Env vars: `PORT`, `PYTHONUNBUFFERED`
- `pei-frontend`
	- Dockerfile: `frontend/Dockerfile`
	- Env vars: `PORT`, `NEXT_PUBLIC_API_BASE_URL`

## API Health Endpoints

- `GET /healthz`
- `GET /health`

## Troubleshooting

- Frontend cannot reach backend:
	- Confirm backend is running on `10000`.
	- Confirm `NEXT_PUBLIC_API_BASE_URL` points to the correct backend URL.
- CORS issues:
	- Set `ALLOWED_ORIGINS` on backend to include the frontend origin.
- Build-time Next.js route errors:
	- Client components using router search params must be wrapped by `Suspense` in server layout boundaries.
