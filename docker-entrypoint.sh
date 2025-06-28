#!/bin/bash
set -e

# Function to wait for database to be ready
wait_for_db() {
    echo "Waiting for PostgreSQL to become available..."
    until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' >/dev/null 2>&1; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "PostgreSQL is up and running!"
}

# Function to wait for Redis to be ready
wait_for_redis() {
    echo "Waiting for Redis to become available..."
    until redis-cli -h redis -a "$REDIS_PASSWORD" ping &>/dev/null; do
        echo "Redis is unavailable - sleeping"
        sleep 1
    done
    echo "Redis is up and running!"
}

# Function to run database migrations
run_migrations() {
    echo "Running database migrations..."
    alembic upgrade head
}

# Function to initialize the database
init_db() {
    echo "Initializing database..."
    python -m app.db.init_db
}

# Function to start the application
start_application() {
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "Starting production server..."
        exec uvicorn \
            --host 0.0.0.0 \
            --port 8000 \
            --workers $((2 * $(nproc) + 1)) \
            --worker-class uvicorn.workers.UvicornWorker \
            --no-access-log \
            --proxy-headers \
            --forwarded-allow-ips="*" \
            --log-level $LOG_LEVEL \
            app.main:app
    else
        echo "Starting development server..."
        exec uvicorn \
            --host 0.0.0.0 \
            --port 8000 \
            --reload \
            --reload-dir /app \
            --reload-include "*.py" \
            --log-level $LOG_LEVEL \
            app.main:app
    fi
}

# Main execution
main() {
    # Wait for dependencies
    wait_for_db
    wait_for_redis
    
    # Run migrations and initialize database
    run_migrations
    init_db
    
    # Start the application
    start_application
}

# Execute main function
main "$@"
