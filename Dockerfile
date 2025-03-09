# syntax = docker/dockerfile:1

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create a temporary directory if needed
RUN mkdir -p /app/temp

# Use a non-root user if desired (optional)
# RUN useradd -m appuser && chown -R appuser:appuser /app
# USER appuser

# Define the start command
CMD ["python", "-m", "app.main"]
