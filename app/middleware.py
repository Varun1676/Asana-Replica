from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from collections import defaultdict, deque

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asana_replica")

# Rate Limit Config
RATE_LIMIT_DURATION = 60  # seconds
RATE_LIMIT_REQUESTS = 100 # requests per duration

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Store request timestamps per IP
        # Using deque to efficiently remove old timestamps
        self.request_history = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        history = self.request_history[client_ip]
        
        # Remove timestamps older than the duration window
        while history and history[0] < now - RATE_LIMIT_DURATION:
            history.popleft()
            
        # Check limit
        if len(history) >= RATE_LIMIT_REQUESTS:
            return Response(
                content="Rate limit exceeded. Please try again later.", 
                status_code=429
            )
            
        # Record this request
        history.append(now)
        
        # Process request
        response = await call_next(request)
        return response

class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - Completed in {process_time:.4f}s")
        
        return response
