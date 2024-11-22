#!/bin/sh

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
  echo "Still waiting for database..."
done

echo "Database is ready!"

# Wait a bit more for PostgreSQL to be fully ready
sleep 5

echo "Running migrations..."
# Run migrations
alembic upgrade head

echo "Starting FastAPI application..."
# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000