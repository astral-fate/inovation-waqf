import os
import sys
import logging
from app import create_app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

try:
    # Create the application instance
    application = create_app()
    logger.info("Application created successfully")
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
