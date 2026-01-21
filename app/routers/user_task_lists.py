from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['User task lists'])


@router.get("/user_task_lists/{user_task_list_gid}", response_model=dict | None, summary="Get a user task list")
async def getusertasklist(request: Request):
    # Implementation pending
    return {}


@router.get("/users/{user_gid}/user_task_list", response_model=dict | None, summary="Get a user's task list")
async def getusertasklistforuser(request: Request):
    # Implementation pending
    return {}

