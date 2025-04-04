FROM python:3.12-slim

# Install system dependencies
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

# Ensure the SQLite database file is writable
RUN chmod 666 waqf.db

# Make sure directories exist for file uploads
RUN mkdir -p static/uploads/projects static/uploads/profiles static/images
RUN chmod -R 777 static/uploads

# Make our start script executable
RUN chmod +x start.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=wsgi.py
ENV PORT=8080

# Use our start script
CMD ["/app/start.sh"]
