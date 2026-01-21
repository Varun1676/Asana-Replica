from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Project templates'])


@router.get("/project_templates/{project_template_gid}", response_model=dict | None, summary="Get a project template")
async def getprojecttemplate(request: Request):
    # Implementation pending
    return {}


@router.delete("/project_templates/{project_template_gid}", response_model=dict | None, summary="Delete a project template")
async def deleteprojecttemplate(request: Request):
    # Implementation pending
    return {}


@router.get("/project_templates", response_model=dict | None, summary="Get multiple project templates")
async def getprojecttemplates(request: Request):
    # Implementation pending
    return {}


@router.get("/teams/{team_gid}/project_templates", response_model=dict | None, summary="Get a team's project templates")
async def getprojecttemplatesforteam(request: Request):
    # Implementation pending
    return {}


@router.post("/project_templates/{project_template_gid}/instantiateProject", response_model=dict | None, summary="Instantiate a project from a project template")
async def instantiateproject(request: Request):
    # Implementation pending
    return {}

