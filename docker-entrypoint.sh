#!/bin/bash
set -e

echo "⏳ Waiting for MySQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "✅ MySQL is ready"

echo "⏳ Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "✅ Redis is ready"

echo "🚀 Running database migrations..."
alembic upgrade head

echo "🎯 Starting application..."
exec "$@"