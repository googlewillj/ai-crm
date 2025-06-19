# Flask CRM Application

A simple CRM application built with Flask, supporting customer record display from a database.
The application is containerized using Docker and includes a GitHub Actions workflow for CI/CD.

## Features

- Display customer records (Full Name, Preferred Name, Zip Code, Birth Date, Email).
- Database integration using Flask-SQLAlchemy and Flask-Migrate.
- Dockerized for easy deployment and testing.
- Automated testing with pytest.
- GitHub Actions for CI.
- JSON API endpoint for customer details (e.g., `/api/customer/<id>`).

## Project Structure

```
/
|-- app/                          # Main application package
|   |-- static/                   # Static files (CSS, JS, images)
|   |   |-- css/style.css
|   |-- templates/                # HTML templates
|   |   |-- base.html
|   |   |-- customers.html
|   |   |-- customer_detail.html
|   |-- __init__.py               # Application factory
|   |-- models.py                 # Database models
|   |-- routes.py                 # Application routes
|-- migrations/                   # Database migration scripts
|-- tests/                        # Test suite
|   |-- conftest.py               # Pytest fixtures and config
|   |-- test_app.py               # Application tests
|-- .github/workflows/            # GitHub Actions workflows
|   |-- main.yml
|-- config.py                     # Configuration settings
|-- Dockerfile                    # Docker configuration
|-- boot.sh                       # Entrypoint script for Docker
|-- main.py                       # Main application script (runner)
|-- requirements.txt              # Python dependencies
|-- README.md                     # This file
```

## Setup and Running Locally

### Prerequisites

- Python 3.10+
- pip
- virtualenv (recommended)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory or set environment variables directly:
    ```env
    FLASK_APP=main.py
    # For local development, it will use app.db (SQLite) by default.
    # To use PostgreSQL, set DATABASE_URL, e.g.:
    # DATABASE_URL=postgresql://user:password@host:port/dbname
    SECRET_KEY=your_very_secret_key
    ```
    If you don't create a `.env` file, `config.py` defaults to an SQLite database named `app.db`.

5.  **Initialize the database and apply migrations:**
    ```bash
    export FLASK_APP=main.py # if not set in .env or shell profile
    flask db upgrade
    ```
    (If `flask` command is not found, you might need to use `python -m flask db upgrade`)

### Running the Application Locally

```bash
flask run
```
The application will be available at `http://127.0.0.1:5000`.

### Running Tests Locally

```bash
export FLASK_APP=main.py # if not set in .env or shell profile
pytest tests/
```

## Running with Docker

### Prerequisites

- Docker installed and running.

### Build the Docker Image

```bash
docker build -t crm-app .
```

### Run the Docker Container

1.  **Using SQLite (default, data stored in `app.db` within the container):**
    The `boot.sh` script will create/upgrade `app.db` inside the container.
    ```bash
    docker run -d -p 5000:5000 --name crm-container crm-app
    ```
    Application will be at `http://localhost:5000`. Data will persist as long as the container volume is not destroyed.

2.  **Using an external PostgreSQL database:**

    First, ensure you have a PostgreSQL instance running. For example, using Docker:
    ```bash
    docker run -d --name crm-postgres \
      -e POSTGRES_USER=crmuser \
      -e POSTGRES_PASSWORD=crmpassword \
      -e POSTGRES_DB=crmdb \
      -p 5432:5432 \
      postgres:13-alpine
    ```

    Then, run the application container. You'll need to provide the `DATABASE_URL`.
    If PostgreSQL is running on the same Docker host, you can often use `host.docker.internal` (on Docker Desktop) or your machine's IP.
    ```bash
    docker run -d -p 8000:5000 \
      --name crm-app-container \
      -e FLASK_APP="main.py" \
      -e SECRET_KEY="a_very_secret_docker_key" \
      -e DATABASE_URL="postgresql://crmuser:crmpassword@host.docker.internal:5432/crmdb" \
      crm-app
    ```
    Application will be at `http://localhost:8000`. The `boot.sh` script in the container will attempt to run `flask db upgrade` against this `DATABASE_URL`.

### Running Tests with Docker (as per GitHub Actions)

The GitHub Actions workflow (`.github/workflows/main.yml`) provides a good example. It runs tests inside the built Docker container, connecting to a PostgreSQL service also managed by Actions.

To replicate locally:
1.  Ensure your Docker image `crm-app` is built.
2.  Ensure you have a PostgreSQL instance for testing (e.g., the `crm-postgres` container from above, or another one).
3.  Run the tests:
    ```bash
    docker run \
      --network="host" \ # Simplest for connecting to localhost postgres; or use a shared Docker network
      -e DATABASE_URL="postgresql://testuser:testpassword@localhost:5432/testdb" \
      -e FLASK_APP="main.py" \
      -e SECRET_KEY="ci_secret_key_local_test" \
      crm-app pytest tests/
    ```
    This command executes `pytest tests/` *inside* the `crm-app` container. The `boot.sh` entrypoint script will first attempt database migrations using the provided `DATABASE_URL`, then execute the `pytest` command.
    **Note:** The `testuser`, `testpassword`, and `testdb` should match your test PostgreSQL setup. The GitHub Actions workflow uses these credentials for its service DB.

## GitHub Actions CI

The workflow in `.github/workflows/main.yml` automatically:
1. Checks out the code.
2. Sets up Python (for any host-level script execution if needed, though most happens in Docker).
3. Builds the Docker image.
4. Starts a PostgreSQL service container.
5. Runs `pytest` tests *inside* the application's Docker container, with the `DATABASE_URL` configured to connect to the PostgreSQL service.

This ensures that the application and its tests are validated in a containerized environment that closely mirrors a potential production setup.
The `boot.sh` script inside the Docker container handles database migrations before running the application or tests.

## API Endpoints

-   `GET /api/customer/<customer_id>`: Retrieves details for a specific customer in JSON format.
    -   **Success Response (200 OK):**
        ```json
        {
          "id": 1,
          "full_name": "John Doe",
          "preferred_name": "John",
          "zip_code": "12345",
          "birth_date": "1990-01-15",
          "email": "john.doe@example.com",
          "created_at": "2023-01-01T10:00:00Z"
        }
        ```
    -   **Error Response (404 Not Found):**
        ```json
        {
          "error": "Customer not found"
        }
        ```
