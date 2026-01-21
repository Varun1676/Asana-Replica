from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Project memberships'])


@router.get("/project_memberships/{project_membership_gid}", response_model=dict | None, summary="Get a project membership")
async def getprojectmembership(request: Request):
    # Implementation pending
    return {}


@router.get("/projects/{project_gid}/project_memberships", response_model=dict | None, summary="Get memberships from a project")
async def getprojectmembershipsforproject(request: Request):
    # Implementation pending
    return {}

