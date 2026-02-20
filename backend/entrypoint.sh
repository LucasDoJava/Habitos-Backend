#!/bin/sh

echo "⏳ Waiting for MySQL..."

while ! nc -z db 3306; do
  sleep 1
done

echo "✅ MySQL is up!"

echo "🔄 Running migrations..."
flask db upgrade

echo "🚀 Starting Flask..."
flask run --host=0.0.0.0 --port=5000
