#!/bin/sh
set -e # Exit immediately if a command exits with a non-zero status.

# Activate virtual environment if it exists and is used in the Docker image
# (Not strictly necessary if using system Python in Docker and installed packages globally,
# but good practice if a venv is part of the Docker build process)
# . /app/venv/bin/activate

echo "Running database migrations..."
# Ensure FLASK_APP is set, though it should be by Dockerfile ENV
export FLASK_APP=${FLASK_APP:-main.py}

# Wait for DB if needed (simple version, more robust checks might be needed for production)
# This is a very basic check for Postgres.
if [ -n "$DATABASE_URL" ] && echo "$DATABASE_URL" | grep -q "postgresql"; then
    db_host=$(echo $DATABASE_URL | awk -F[@/] '{print $4}' | awk -F: '{print $1}')
    db_port=$(echo $DATABASE_URL | awk -F[@/] '{print $4}' | awk -F: '{print $2}')
    counter=0
    echo "Waiting for database at $db_host:$db_port..."
    while ! nc -z $db_host $db_port; do
        sleep 1
        counter=$((counter+1))
        if [ $counter -ge 30 ]; then
            echo "Database not available after 30 seconds. Exiting."
            exit 1
        fi
    done
    echo "Database is up."
fi

flask db upgrade
echo "Database migrations complete."

# If arguments are passed to boot.sh (e.g., `pytest tests/`), execute them.
# Otherwise, start the Flask application with Gunicorn.
if [ $# -gt 0 ]; then
    echo "Executing command: $@"
    exec "$@"
else
    echo "Starting Gunicorn server..."
    # exec gunicorn --bind 0.0.0.0:5000 main:app
    # For development/testing, flask run might be sufficient if Gunicorn isn't explicitly needed by the run command.
    # The Dockerfile CMD was originally flask run. If Gunicorn is preferred, ensure it's in requirements.txt.
    # The GitHub workflow passes `pytest tests/` as a command, so that will be run instead of Gunicorn in CI.
    exec flask run --host=0.0.0.0 --port=5000
fi
