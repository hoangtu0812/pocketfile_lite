# ─── Stage 1: Builder ─────────────────────────────────────────
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# We avoid apt-get/apk completely because some Portainer environments 
# block OS-level package repository access or lack IPv6 DNS routing.
# All our Python dependencies (bcrypt, psycopg2-binary, PyJWT) provide 
# pre-compiled wheels for modern Linux architectures.
COPY requirements.txt .
# Setting pip parameters to bypass LXC DNS and Timeout drop issues
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install -r requirements.txt

# ─── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser \
    && mkdir -p /storage && chown -R appuser:appgroup /app /storage

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/api/docs || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
