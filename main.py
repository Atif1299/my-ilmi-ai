import uvicorn
import logging
import sys

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting FastAPI backend on port 8000...")

    try:
        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=8000,
            workers=1,
            reload=False
        )
    except Exception as e:
        logging.error(f"Failed to start FastAPI: {e}")
        sys.exit(1)