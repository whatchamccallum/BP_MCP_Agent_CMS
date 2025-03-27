#!/bin/bash
# scripts/init_and_migrate.sh
# Database initialization and migration script

set -e

# Set the environment
export FLASK_ENV=${FLASK_ENV:-development}

echo "Running database initialization and migrations..."
python init_db.py

# If alembic.ini exists, run migrations
if [ -f alembic.ini ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

echo "Database setup completed successfully!"
