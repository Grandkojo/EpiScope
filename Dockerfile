# Use official Python base image (much smaller than Ubuntu)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

RUN pip install --upgrade setuptools
# Install system dependencies only once
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to cache dependencies
COPY requirements.txt .

# Install Python packages
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# Copy app source code
COPY . .

# Expose port
EXPOSE 8000

# Run Gunicorn server
CMD ["gunicorn", "episcope.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

