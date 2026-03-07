# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for mysqlclient and builds
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app/

# Create virtual environment
RUN python -m venv venv

# Install Python dependencies
RUN . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# Expose Django port
EXPOSE 8000

# Run Django server
CMD ["venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]