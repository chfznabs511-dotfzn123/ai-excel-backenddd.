# Lightweight Python image
FROM python:3.11.9-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run Gunicorn with 1 worker for free tier
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 app:app

