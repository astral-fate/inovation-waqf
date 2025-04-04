FROM python:3.12-slim

# Install system dependencies for Pillow and PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libpq-dev

WORKDIR /app

# Copy requirements and install dependencies 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the app with better logging
CMD gunicorn --log-level debug --capture-output --enable-stdio-inheritance --bind 0.0.0.0:${PORT:-8000} wsgi:application
