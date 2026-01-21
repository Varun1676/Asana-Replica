from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Sections'])


@router.get("/sections/{section_gid}", response_model=dict | None, summary="Get a section")
async def getsection(request: Request):
    # Implementation pending
    return {}


@router.put("/sections/{section_gid}", response_model=dict | None, summary="Update a section")
async def updatesection(request: Request):
    # Implementation pending
    return {}


@router.delete("/sections/{section_gid}", response_model=dict | None, summary="Delete a section")
async def deletesection(request: Request):
    # Implementation pending
    return {}


@router.get("/projects/{project_gid}/sections", response_model=dict | None, summary="Get sections in a project")
async def getsectionsforproject(request: Request):
    # Implementation pending
    return {}


@router.post("/projects/{project_gid}/sections", response_model=dict | None, summary="Create a section in a project")
async def createsectionforproject(request: Request):
    # Implementation pending
    return {}


@router.post("/sections/{section_gid}/addTask", response_model=dict | None, summary="Add task to section")
async def addtaskforsection(request: Request):
    # Implementation pending
    return {}


@router.post("/projects/{project_gid}/sections/insert", response_model=dict | None, summary="Move or Insert sections")
async def insertsectionforproject(request: Request):
    # Implementation pending
    return {}

