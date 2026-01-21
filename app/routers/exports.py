from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Exports'])


@router.post("/exports/graph", response_model=dict | None, summary="Initiate a graph export")
async def creategraphexport(request: Request):
    # Implementation pending
    return {}


@router.post("/exports/resource", response_model=dict | None, summary="Initiate a resource export")
async def createresourceexport(request: Request):
    # Implementation pending
    return {}

