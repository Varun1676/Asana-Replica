from fastapi import FastAPI, Depends
from app.database import create_db_and_tables
import os
import importlib
from pathlib import Path
from app.middleware import RateLimitMiddleware, ProcessTimeMiddleware
from app.auth import verify_token

app = FastAPI(
    title="Asana Replica API",
    description="A replica of the Asana API based on the OpenAPI specification.",
    version="1.0.0",
    # Apply Auth Globally (except for openapi.json/docs which are excluded by default if not secured explicitly)
    # Note: This means EVERY request needs a token.
    dependencies=[Depends(verify_token)]
)

# Register Middleware (LIFO order: RateLimit runs first if added last? No, middleware is wrapped. 
# Added last = outer layer = runs first)
app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(RateLimitMiddleware)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Dynamically include all routers
routers_dir = Path(__file__).parent / "routers"

# DEBUG: Explicit import to force error visibility
# try:
#     from app.routers import users
#     app.include_router(users.router)
#     print("DEBUG: Users router loaded successfully")
# except Exception as e:
#     print(f"DEBUG: Failed to load users router explicitly: {e}")
#     # Re-raise to crash app if crucial
#     raise e

for filename in os.listdir(routers_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"app.routers.{filename[:-3]}"
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "router"):
                app.include_router(module.router)
                print(f"Loaded router: {module_name}")
        except Exception as e:
            # CHANGED: Use logger or force print flush
            print(f"CRITICAL ERROR: Failed to load router {module_name}: {e}", flush=True)

@app.get("/", dependencies=[]) # Override global dependency to allow health check without auth if needed? No, let's keep it strict or allow it.
def root():
    return {"message": "Asana Replica API is running. Check /docs for API documentation."}