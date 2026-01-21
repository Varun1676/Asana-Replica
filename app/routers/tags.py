from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Tags'])


@router.get("/tags", response_model=dict | None, summary="Get multiple tags")
async def gettags(request: Request):
    # Implementation pending
    return {}


@router.post("/tags", response_model=dict | None, summary="Create a tag")
async def createtag(request: Request):
    # Implementation pending
    return {}


@router.get("/tags/{tag_gid}", response_model=dict | None, summary="Get a tag")
async def gettag(request: Request):
    # Implementation pending
    return {}


@router.put("/tags/{tag_gid}", response_model=dict | None, summary="Update a tag")
async def updatetag(request: Request):
    # Implementation pending
    return {}


@router.delete("/tags/{tag_gid}", response_model=dict | None, summary="Delete a tag")
async def deletetag(request: Request):
    # Implementation pending
    return {}


@router.get("/tasks/{task_gid}/tags", response_model=dict | None, summary="Get a task's tags")
async def gettagsfortask(request: Request):
    # Implementation pending
    return {}


@router.get("/workspaces/{workspace_gid}/tags", response_model=dict | None, summary="Get tags in a workspace")
async def gettagsforworkspace(request: Request):
    # Implementation pending
    return {}


@router.post("/workspaces/{workspace_gid}/tags", response_model=dict | None, summary="Create a tag in a workspace")
async def createtagforworkspace(request: Request):
    # Implementation pending
    return {}

