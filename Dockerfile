# Base image
FROM python:3.11.9-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Bind Gunicorn to Render's dynamic port
CMD gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app
