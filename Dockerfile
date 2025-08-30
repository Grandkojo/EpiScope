# Use multi-stage build with Debian security updates
FROM python:3.12-slim as builder

# Install build dependencies and security updates
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y \
        gcc \
        g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies with security updates
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

# Install security updates and runtime dependencies
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . /app
WORKDIR /app

# Install gunicorn
RUN pip install --no-cache-dir gunicorn

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "episcope.wsgi:application"]