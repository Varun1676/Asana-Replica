from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Project statuses'])


@router.get("/project_statuses/{project_status_gid}", response_model=dict | None, summary="Get a project status")
async def getprojectstatus(request: Request):
    # Implementation pending
    return {}


@router.delete("/project_statuses/{project_status_gid}", response_model=dict | None, summary="Delete a project status")
async def deleteprojectstatus(request: Request):
    # Implementation pending
    return {}


@router.get("/projects/{project_gid}/project_statuses", response_model=dict | None, summary="Get statuses from a project")
async def getprojectstatusesforproject(request: Request):
    # Implementation pending
    return {}


@router.post("/projects/{project_gid}/project_statuses", response_model=dict | None, summary="Create a project status")
async def createprojectstatusforproject(request: Request):
    # Implementation pending
    return {}

