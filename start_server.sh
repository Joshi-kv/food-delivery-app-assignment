#!/bin/bash

# Food Delivery App - Server Startup Script
# This script starts the Django application with Daphne (ASGI server) for WebSocket support

echo "=========================================="
echo "Food Delivery App - Starting Server"
echo "=========================================="
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Set environment variable to disable autobahn NVX (prevents _nvx_utf8validator error)
export AUTOBAHN_USE_NVX=0

# Check if Redis is running
echo "Checking Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "✗ Redis is not running!"
    echo "Please start Redis with: brew services start redis"
    echo "Or: redis-server"
    exit 1
fi

# Run migrations (if any pending)
echo ""
echo "Checking for pending migrations..."
python manage.py migrate --check > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Running migrations..."
    python manage.py migrate
fi

# Collect static files (optional, for production)
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

echo ""
echo "=========================================="
echo "Starting Daphne ASGI Server"
echo "=========================================="
echo "Server will be available at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start Daphne with AUTOBAHN_USE_NVX=0 to prevent _nvx_utf8validator error
# You can copy and run this command directly in your terminal:
AUTOBAHN_USE_NVX=0 daphne -b 127.0.0.1 -p 8000 food_delivery_app.asgi:application

