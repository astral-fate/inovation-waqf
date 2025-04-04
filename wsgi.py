import os
import sys
import logging
from app import create_app

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Print environment variables for debugging
logger.info(f"PORT environment variable: {os.environ.get('PORT', 'not set')}")
logger.info(f"All environment variables: {dict(os.environ)}")

try:
    # Create the application instance
    logger.info("Creating application...")
    application = create_app()
    logger.info("Application created successfully")
    
    # Add middleware to log all requests
    class RequestLoggingMiddleware:
        def __init__(self, app):
            self.app = app
            
        def __call__(self, environ, start_response):
            method = environ.get('REQUEST_METHOD', 'UNKNOWN')
            path = environ.get('PATH_INFO', 'UNKNOWN')
            query = environ.get('QUERY_STRING', '')
            
            if query:
                full_path = f"{path}?{query}"
            else:
                full_path = path
                
            logger.info(f"Request: {method} {full_path}")
            
            def custom_start_response(status, headers, exc_info=None):
                logger.info(f"Response: {status}")
                return start_response(status, headers, exc_info)
            
            try:
                return self.app(environ, custom_start_response)
            except Exception as e:
                logger.error(f"Error handling request {method} {full_path}: {str(e)}", exc_info=True)
                status = '500 Internal Server Error'
                response_headers = [('Content-type', 'text/plain')]
                start_response(status, response_headers)
                return [b'An error occurred processing your request']
    
    # Wrap the application with the middleware
    application.wsgi_app = RequestLoggingMiddleware(application.wsgi_app)
    
except Exception as e:
    logger.error(f"Failed to create application: {str(e)}", exc_info=True)
    raise

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 8080))
        logger.info(f"Starting application on port {port}")
        application.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Failed to run application: {str(e)}", exc_info=True)
        raise
