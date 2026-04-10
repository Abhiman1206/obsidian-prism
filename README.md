# Predictive Engineering Intelligence Platform

Containerized backend and frontend for deployment on Render.

## Services

- Backend: FastAPI app on port 10000
- Frontend: Next.js app on port 3000

## Local Validation

Backend tests:

- Set PYTHONPATH=backend
- Run: pytest backend/tests -q

Frontend type checks:

- Run from frontend: npm run typecheck

## Container Build Commands

- docker build -f backend/Dockerfile backend
- docker build -f frontend/Dockerfile frontend

## Render Deployment

This repository includes render.yaml with two web services:

- pei-backend: backend/Dockerfile, health check path /healthz
- pei-frontend: frontend/Dockerfile

Required environment variables:

- PORT
- NEXT_PUBLIC_API_BASE_URL

## Runtime Health

- /health
- /healthz
