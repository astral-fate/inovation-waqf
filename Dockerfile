FROM python:3.12-slim

# Install system dependencies for Pillow and SQLite
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libpq-dev \
    sqlite3

WORKDIR /app

# Copy requirements and install dependencies 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Make sure directories exist for file uploads
RUN mkdir -p static/uploads/projects static/uploads/profiles static/images

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=wsgi.py
ENV DATABASE_URL=sqlite:///waqf.db
ENV SECRET_KEY=your_secure_key_here

# Run the app with better logging
CMD gunicorn --log-level debug --workers 1 --threads 8 --timeout 120 --capture-output --enable-stdio-inheritance --bind 0.0.0.0:${PORT:-8000} wsgi:application
