# Adaptive Homework Assignments

Web application prototype for adaptive homework assignment and student progress analysis.

## Current State

This repository now reflects an integrated checkpoint of roughly `60%` completion:

- substantial FastAPI backend with authentication, role-based access control, homework management, adaptive self-education recommendation, submission processing, and progress analytics
- frontend MVP for both student and teacher roles with separate `Homeworks` and `Self-Education` flows
- demo-ready seeded data and fallback-friendly UI flows
- academic progress report stored in `docs/report/Adaptive_Homework_60_percent_report.md`

## Repository Structure

```text
backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
  seed.py
frontend/
  src/
    api/
    components/
    context/
    pages/
docs/
  plans/
  report/
```

## Demo Accounts

- Student: `student@example.com` / `demo123`
- Teacher: `teacher@example.com` / `demo123`

## Main MVP Flows

- Student: dashboard, assigned homeworks, homework detail, self-education, progress
- Teacher: dashboard, homework builder with assignees and items, task bank, student analytics

## Backend Run

From the repository root:

```bash
PYTHONPATH=backend .venv/bin/python -m uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

Seed demo data manually if needed:

```bash
PYTHONPATH=backend .venv/bin/python backend/seed.py
```

## Frontend Run

```bash
cd frontend
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000` by default. You can override it with `VITE_API_BASE_URL`.

## Verification

Backend tests:

```bash
PYTHONPATH=backend .venv/bin/python -m unittest discover -s backend/tests -v
```

Frontend production build:

```bash
cd frontend
npm run build
```
