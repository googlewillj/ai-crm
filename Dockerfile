# Start with a Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for psycopg2 and other potential needs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make the boot script executable
RUN chmod +x boot.sh

# Set the FLASK_APP environment variable
ENV FLASK_APP main.py

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application
ENTRYPOINT ["./boot.sh"]
# CMD ["flask", "run", "--host=0.0.0.0"]
# CMD will be handled by boot.sh to allow for db migrations first
