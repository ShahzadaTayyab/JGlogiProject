# Use an official Python image as the base
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-traditional \
    build-essential \
    libpq-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
