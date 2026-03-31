FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY pytest.ini ./pytest.ini
COPY README.md ./README.md

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "loan_agents.runtime.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
