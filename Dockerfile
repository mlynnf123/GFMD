# GFMD Email Automation - Production Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional production dependencies
RUN pip install --no-cache-dir gunicorn flask

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 gfmduser && chown -R gfmduser:gfmduser /app
USER gfmduser

# Set environment variables
ENV PYTHONPATH=/app
ENV TOKENIZERS_PARALLELISM=false
ENV PYTHONUNBUFFERED=1

# Expose port (for health checks and potential web interface)
EXPOSE 8080

# Start the health server which will launch the scheduler internally
CMD ["python3", "health_server.py"]