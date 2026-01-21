from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Custom field settings'])


@router.get("/projects/{project_gid}/custom_field_settings", response_model=dict | None, summary="Get a project's custom fields")
async def getcustomfieldsettingsforproject(request: Request):
    # Implementation pending
    return {}


@router.get("/portfolios/{portfolio_gid}/custom_field_settings", response_model=dict | None, summary="Get a portfolio's custom fields")
async def getcustomfieldsettingsforportfolio(request: Request):
    # Implementation pending
    return {}


@router.get("/goals/{goal_gid}/custom_field_settings", response_model=dict | None, summary="Get a goal's custom fields")
async def getcustomfieldsettingsforgoal(request: Request):
    # Implementation pending
    return {}


@router.get("/teams/{team_gid}/custom_field_settings", response_model=dict | None, summary="Get a team's custom fields")
async def getcustomfieldsettingsforteam(request: Request):
    # Implementation pending
    return {}

