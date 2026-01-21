from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Task templates'])


@router.get("/task_templates", response_model=dict | None, summary="Get multiple task templates")
async def gettasktemplates(request: Request):
    # Implementation pending
    return {}


@router.get("/task_templates/{task_template_gid}", response_model=dict | None, summary="Get a task template")
async def gettasktemplate(request: Request):
    # Implementation pending
    return {}


@router.delete("/task_templates/{task_template_gid}", response_model=dict | None, summary="Delete a task template")
async def deletetasktemplate(request: Request):
    # Implementation pending
    return {}


@router.post("/task_templates/{task_template_gid}/instantiateTask", response_model=dict | None, summary="Instantiate a task from a task template")
async def instantiatetask(request: Request):
    # Implementation pending
    return {}

