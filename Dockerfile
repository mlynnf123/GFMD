# Use Python 3.9 slim image for compatibility
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_google_sheets.txt
RUN pip install --no-cache-dir -r requirements_api.txt

# Install production WSGI server
RUN pip install --no-cache-dir gunicorn

# Copy application code
COPY *.py ./
COPY *.json ./
COPY *.csv ./

# Copy Gmail credentials and token if they exist
RUN if [ -f gmail_credentials.json ]; then echo "Gmail credentials found"; fi
RUN if [ -f gmail_token.json ]; then echo "Gmail token found"; fi

# Create directories for credentials and logs
RUN mkdir -p /app/credentials /app/logs /home/appuser/.config/gspread

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
# Gmail credentials will be set via Cloud Run environment variables
# ENV GMAIL_ADDRESS="your-email@gmail.com"
# ENV GMAIL_APP_PASSWORD="your-app-password"

# Cloud Run runs as a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
# Copy Google Sheets credentials to gspread default location (if exists)
RUN if [ -f /app/google_sheets_credentials.json ]; then \
        cp /app/google_sheets_credentials.json /home/appuser/.config/gspread/service_account.json && \
        chown appuser:appuser /home/appuser/.config/gspread/service_account.json; \
    else \
        echo "Google Sheets credentials not found, skipping..."; \
    fi
USER appuser

# Expose port
EXPOSE 8080

# Gunicorn already installed above

# Start the Flask app with gunicorn - increased concurrency
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 3600 --worker-class gthread main:app