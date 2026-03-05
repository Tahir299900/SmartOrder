# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (like libpq-dev for PostgreSQL support)
RUN apt-get update && apt-get install -y libpq-dev

# Copy the current directory contents into the container
COPY . /app/

# Set up the virtual environment and upgrade pip
RUN python -m venv venv
RUN . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# Expose port 8000 to access the Django app
EXPOSE 8000

# Run the Django development server (adjust if using production settings)
CMD [".venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]