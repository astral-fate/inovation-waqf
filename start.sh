#!/bin/bash
# start.sh - Wrapper script to ensure correct port binding

echo "Starting application with PORT=$PORT"
gunicorn --log-level debug --workers 1 --threads 4 --timeout 120 --access-logfile - --error-logfile - --bind 0.0.0.0:8080 wsgi:application
