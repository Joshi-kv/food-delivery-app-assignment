# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AUTOBAHN_USE_NVX=0

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Create directories for SQLite and media files
RUN mkdir -p /app/data /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 80
EXPOSE 80

# Run the application on port 80
CMD ["daphne", "-b", "0.0.0.0", "-p", "80", "food_delivery_app.asgi:application"]
