# syntax = docker/dockerfile:1

FROM python:3.10-slim

# Update package lists and install OpenVPN, its dependencies and Playwright system dependencies
RUN apt-get update && \
    apt-get install -y \
        curl \
        fonts-liberation \
        gnupg2 \
        libappindicator3-1 \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libgtk-3-0 \
        libnss3 \
        libpangocairo-1.0-0 \
        libxss1 \
        openvpn && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable so that Playwright uses local installation for browsers
ENV PLAYWRIGHT_BROWSERS_PATH=0

# Install Playwright system dependencies (if needed) using playwright's helper script
# This installs additional libraries required by the browsers.
RUN python -m playwright install-deps && python -m playwright install

# Copy application source code
COPY . .

# (Optional) Create required directories and set permissions (similar to your Node.js Dockerfile)
RUN mkdir -p /app/temp /app/services && \
    touch /app/services/auth.txt && \
    chmod 600 /app/services/auth.txt && \
    if [ -e /dev/net/tun ]; then chmod 600 /dev/net/tun; fi

# Define the start command
CMD ["python", "-m", "app.main"]
