FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Phoenix code
COPY phoenix/ ./phoenix/

# Create directories
RUN mkdir -p /app/data /app/workspaces /app/logs

# Expose API port
EXPOSE 8000

# Run Phoenix API
CMD ["python", "-m", "phoenix.api.main"]
