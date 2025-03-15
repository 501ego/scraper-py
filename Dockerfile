# syntax = docker/dockerfile:1

FROM python:3.10-slim

# Update package lists and install OpenVPN (and any required dependencies)
RUN apt-get update && \
    apt-get install -y openvpn && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .


# (Optional) Create the services directory if your config files are located there.
# This is similar to your Node.js Dockerfile, ensuring that auth.txt exists and has proper permissions.
RUN mkdir -p /app/temp && mkdir -p /app/services && \
    touch /app/services/auth.txt && \
    chmod 600 /app/services/auth.txt && \
    # Adjust /dev/net/tun permissions if available
    if [ -e /dev/net/tun ]; then chmod 600 /dev/net/tun; fi

# Define the start command
CMD ["python", "-m", "app.main"]
