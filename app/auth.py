from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

# Simple Bearer scheme
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies that a Bearer token is present.
    In a real app, this would validate the token signature or check against a DB.
    For this replica, we ensure it's provided.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Optional: Log the token or perform rudimentary check
    # if token != "EXPECTED_TOKEN": ...
    return token
