#!/bin/bash

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
while ! mysqladmin ping -h"db" -u"root" -p"root_password" --silent; do
    sleep 1
done

echo "MySQL is ready! Initializing database..."

# Initialize database
mysql -h"db" -u"root" -p"root_password" < /app/init.sql

echo "Database initialized. Starting application..."

# Run the Python application
python3 /app/app.py
