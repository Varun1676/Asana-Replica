from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Reactions'])


@router.get("/reactions", response_model=dict | None, summary="Get reactions with an emoji base on an object.")
async def getreactionsonobject(request: Request):
    # Implementation pending
    return {}

