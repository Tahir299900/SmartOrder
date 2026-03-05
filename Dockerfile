# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev

# Copy the current directory contents into the container
COPY . /app/

# Install Python dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for Django app
EXPOSE 8000

# Run the Django development server (adjust if using production settings)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]