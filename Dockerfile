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

# Copy all files including the database
COPY . .

# Ensure the SQLite database file is writable
RUN chmod 666 waqf.db

# Make sure directories exist for file uploads
RUN mkdir -p static/uploads/projects static/uploads/profiles static/images
RUN chmod -R 777 static/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=wsgi.py
ENV SECRET_KEY=your_secure_key_here

# Add the wsgi.py file if not already present (you can adjust the content as needed)
RUN if [ ! -f wsgi.py ]; then echo 'import os\nimport sys\nimport logging\nfrom app import create_app\n\nlogging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stdout)])\nlogger = logging.getLogger(__name__)\n\ntry:\n    application = create_app()\n    logger.info("Application created successfully")\nexcept Exception as e:\n    logger.error(f"Failed to create application: {str(e)}", exc_info=True)\n    raise\n\nif __name__ == "__main__":\n    try:\n        port = int(os.environ.get("PORT", 8080))\n        logger.info(f"Starting application on port {port}")\n        application.run(host="0.0.0.0", port=port)\n    except Exception as e:\n        logger.error(f"Failed to run application: {str(e)}", exc_info=True)\n        raise' > wsgi.py; fi

# Run the app with better debugging
# Make sure to use the PORT environment variable directly
CMD gunicorn --log-level debug --workers 1 --threads 4 --timeout 120 --capture-output --enable-stdio-inheritance --access-logfile - --error-logfile - --bind 0.0.0.0:${PORT} wsgi:application
