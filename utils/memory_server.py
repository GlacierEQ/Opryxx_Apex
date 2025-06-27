import os
import sys
import time
import logging
import signal
import threading
from concurrent import futures
import grpc

# Add current directory to path to find generated protobuf modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cognitive_core_pb2
import cognitive_core_pb2_grpc

# Configuration
MEMORY_FILE = "cognitive_core_state.pb"
LISTEN_ADDRESS = "[::]:50051"
LOG_FILE = "memory_service.log"
SCHEMA_VERSION = 2

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MemoryServer")

# Import the service implementation
try:
    from memory_service import PersistentCognitionServicer
except ImportError:
    logger.error("Failed to import memory service implementation. Please ensure memory_service.py exists.")
    sys.exit(1)

def serve():
    """Start the gRPC server."""
    # Create server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add services
    service = PersistentCognitionServicer()
    cognitive_core_pb2_grpc.add_PersistentCognitionServiceServicer_to_server(
        service, server
    )
    
    # Start server
    server.add_insecure_port(LISTEN_ADDRESS)
    server.start()
    
    logger.info(f"Server started on {LISTEN_ADDRESS}")
    
    # Handle shutdown
    def handle_shutdown(signum, frame):
        logger.info("Shutting down server...")
        server.stop(0)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Keep server running
    try:
        while True:
            time.sleep(60 * 60 * 24)  # Sleep for a day
    except KeyboardInterrupt:
        handle_shutdown(None, None)

if __name__ == '__main__':
    logger.info("Starting Memory Service...")
    serve()
