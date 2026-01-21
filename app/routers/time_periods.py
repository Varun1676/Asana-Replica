from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Time periods'])


@router.get("/time_periods/{time_period_gid}", response_model=dict | None, summary="Get a time period")
async def gettimeperiod(request: Request):
    # Implementation pending
    return {}


@router.get("/time_periods", response_model=dict | None, summary="Get time periods")
async def gettimeperiods(request: Request):
    # Implementation pending
    return {}

