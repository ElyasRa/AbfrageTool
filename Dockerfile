FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend files
COPY frontend/ ./frontend/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY="change-this-secret-key-in-production-to-something-very-secure"

# Expose port
EXPOSE 8000

# Change to backend directory and run uvicorn
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
