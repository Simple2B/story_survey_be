#!/bin/bash
echo Starting server
mkdir -p app/router/reports
poetry run alembic upgrade head
poetry run uvicorn app.main:app --workers 3 --host 0.0.0.0 --port 80
