# Use a lean Python base image
FROM python:3.10-slim

# Setting environment variables for Python/Django
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# Install system dependencies (postgresql-client for wait script)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy wait script and make executable
COPY wait-for-db.sh /usr/local/bin/wait-for-db.sh
RUN chmod +x /usr/local/bin/wait-for-db.sh

# Copy the entire project code (including donor_project, donor_app, and the 'grpc' folder)
COPY . .

# Expose the port (Django's default internal port)
EXPOSE 8000

# Command: Wait for DB, run migrations, then start server
CMD ["sh", "-c", "/usr/local/bin/wait-for-db.sh db python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]