# 🚀 MediKiosk — DevOps, CI/CD & Deployment Architecture

**Document Version:** `1.1.0-PROD`  
**Status:** Approved for Implementation  
**SIH Problem Statement ID:** `26047`  

---

## 1. Containerized Infrastructure (`docker-compose.yml`)

```yaml
version: "3.8"

services:
  # 1. FastAPI Clinical Intelligence Gateway
  medikiosk-api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - SARVAM_API_KEY=${SARVAM_API_KEY}
      - EKA_CLIENT_ID=${EKA_CLIENT_ID}
      - EKA_CLIENT_SECRET=${EKA_CLIENT_SECRET}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: always

  # 2. Next.js Physician Consultation Portal
  medikiosk-doctor-portal:
    build:
      context: ./doctor_portal
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    restart: always

  # 3. Redis In-Memory State & Rate Limiter
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: always
```

---

## 2. Production Dockerfile Specifications

### 2.1 Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
FROM python:3.12-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## 3. GitHub Actions CI/CD Pipeline (`.github/workflows/deploy.yml`)

```yaml
name: MediKiosk Production CI/CD Pipeline

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]

jobs:
  backend-qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov ruff
      - name: Ruff Linter
        run: ruff check backend/
      - name: Run Clinical Safety Tests
        run: pytest backend/tests --cov=backend

  flutter-kiosk-qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: "3.24.x"
          channel: "stable"
      - name: Install Packages
        run: flutter pub get
        working-directory: ./kiosk_app
      - name: Analyze Flutter
        run: flutter analyze
        working-directory: ./kiosk_app
      - name: Flutter Unit & Widget Tests
        run: flutter test
        working-directory: ./kiosk_app
```
