# ==========================================
# Stage 1: Build Dependencies
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies if needed (psycopg2-binary comes precompiled)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install requirements to a local prefix
RUN pip install --no-cache-dir --user -r requirements.txt


# ==========================================
# Stage 2: Production Runtime
# ==========================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Install runtime database libraries and clean packages cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Add dependencies to PATH
ENV PATH=/root/.local/bin:$PATH

# Add a secure non-privileged system user
RUN groupadd -g 10001 runuser && \
    useradd -u 10001 -g runuser -m -s /bin/bash runuser

# Copy application source code
COPY --chown=runuser:runuser app/ /app/app/
COPY --chown=runuser:runuser alembic/ /app/alembic/
COPY --chown=runuser:runuser alembic.ini /app/

# Switch execution context to non-root user
USER runuser

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# Run the FastAPI app via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
