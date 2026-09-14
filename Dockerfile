# ==========================================
# Stage 1: Build React + TypeScript Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Python Backend Runtime
# ==========================================
FROM python:3.11-slim AS runtime
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for ultra-fast package management
RUN pip install --no-cache-dir uv

# Install Python backend dependencies
COPY backend/requirements.txt ./backend/
RUN uv pip install --no-cache --system -r backend/requirements.txt

# Copy backend source code
COPY backend/src ./backend/src
COPY backend/main.py ./backend/

# Copy built frontend static assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

ENV STATIC_DIR=/app/frontend/dist
ENV PORT=8000
ENV PYTHONPATH=/app/backend

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
