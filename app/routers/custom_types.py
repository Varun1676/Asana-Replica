from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Custom types'])


@router.get("/custom_types", response_model=dict | None, summary="Get all custom types associated with an object")
async def getcustomtypes(request: Request):
    # Implementation pending
    return {}


@router.get("/custom_types/{custom_type_gid}", response_model=dict | None, summary="Get a custom type")
async def getcustomtype(request: Request):
    # Implementation pending
    return {}

