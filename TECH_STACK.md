# Technology Stack

This document outlines the technology stack and tools used in the Loan Agents project across its different layers (Backend, Frontend, Infrastructure, and Tooling).

## 1. Backend

The backend is a robust AI/Agentic Service built handling orchestration, risk assessment, document processing, and compliance.

*   **Language:** Python 3.11
*   **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Version 0.116.1)
*   **ASGI Server:** [Uvicorn](https://www.uvicorn.org/) (Version 0.35.0)
*   **Agentic Frameworks:**
    *   [CrewAI](https://www.crewai.com/) (Integration via adapter)
    *   [LangGraph](https://python.langchain.com/v0.1/docs/langgraph/) (Integration via adapter)
*   **Code Quality & Tooling:**
    *   Formatter & Linter: [Ruff](https://docs.astral.sh/ruff/)
    *   Static Type Checker: [Mypy](https://mypy.readthedocs.io/)
*   **Testing:**
    *   [pytest](https://docs.pytest.org/)
    *   [httpx](https://www.python-httpx.org/) (for FastAPI async test client)

## 2. Frontend

The frontend is a modern Single Page Application (SPA) designed to interact with the backend APIs.

*   **Language:** [TypeScript](https://www.typescriptlang.org/) (Version 5.8)
*   **UI Library:** [React 18](https://react.dev/)
*   **Build Tool:** [Vite](https://vitejs.dev/)
*   **Code Quality:**
    *   Linter: [ESLint](https://eslint.org/) (v9) with `typescript-eslint`
*   **Testing:**
    *   [Vitest](https://vitest.dev/) (Test Runner)
    *   [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
    *   [jsdom](https://github.com/jsdom/jsdom) (DOM simulation environment)

## 3. Infrastructure & Deployment

The system is configured to be containerized and easily deployable across modern cloud platforms.

*   **Containerization:** Docker (`Dockerfile` for the FastAPI backend)
*   **Frontend Hosting:** [Vercel](https://vercel.com/) (configured via `vercel.json`)
*   **Backend Hosting:** [Render](https://render.com/) (configured via `render.yaml`)

## 4. Custom Tooling / CLI

The project also includes a specialized `ui-ux-pro-max-skill` package.

*   **Environment:** Node.js
*   **Purpose:** A custom Command Line Interface (CLI) likely used for scaffolding UI templates, syncing data, and maintaining UI/UX standards within the workspace.
*   **Language:** TypeScript
