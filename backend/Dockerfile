# ─── Stage 1: Builder ─────────────────────────────────────────
FROM python:3.11-alpine AS builder

WORKDIR /build

# Install Python dependencies into a virtual environment
# We install build essentials (gcc, musl-dev) and postgresql-dev because Alpine 
# heavily relies on building from source for packages like psycopg2 or bcrypt.
COPY requirements.txt .
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    python3-dev \
    && python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ─── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.11-alpine AS runtime

WORKDIR /app

# Install required system libraries for psycopg2 to run on Alpine
RUN apk add --no-cache libpq curl

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create non-root user for security (Alpine compatible)
RUN adduser -D -s /bin/sh -h /app appuser \
    && mkdir -p /storage && chown -R appuser:appuser /app /storage

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/api/docs || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
