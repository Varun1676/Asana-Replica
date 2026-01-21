from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from app.database import get_session
from app.db_models import WorkspaceMembership, User, Workspace
from app.models.schemas import *

router = APIRouter(tags=['User task lists'])


@router.get("/user_task_lists/{user_task_list_gid}", response_model=dict | None, summary="Get a user task list")
async def getusertasklist(user_task_list_gid: str, request: Request, session: Session = Depends(get_session)):
    # In this replica, we map UserTaskList 1:1 with WorkspaceMembership for simplicity
    # So user_task_list_gid is expected to be the WorkspaceMembership GID
    membership = session.get(WorkspaceMembership, user_task_list_gid)
    
    if not membership:
        raise HTTPException(status_code=404, detail="User task list not found")
        
    user = session.get(User, membership.user_gid)
    workspace = session.get(Workspace, membership.workspace_gid)
    
    if not user or not workspace:
        raise HTTPException(status_code=404, detail="Related resources not found")

    return {
        "data": {
            "gid": membership.gid, # reusing membership GID as task list GID
            "resource_type": "user_task_list",
            "name": f"My tasks in {workspace.name}",
            "owner": {
                "gid": user.gid,
                "resource_type": "user",
                "name": user.name
            },
            "workspace": {
                "gid": workspace.gid,
                "resource_type": "workspace",
                "name": workspace.name
            }
        }
    }


@router.get("/users/{user_gid}/user_task_list", response_model=dict | None, summary="Get a user's task list")
async def getusertasklistforuser(
    user_gid: str, 
    request: Request,
    workspace: str = None, 
    session: Session = Depends(get_session)
):
    # Find the user
    user = session.get(User, user_gid)
    if not user:
         raise HTTPException(status_code=404, detail="User not found")

    # Build query for membership
    query = select(WorkspaceMembership).where(WorkspaceMembership.user_gid == user_gid)
    
    if workspace:
        query = query.where(WorkspaceMembership.workspace_gid == workspace)
    
    memberships = session.exec(query).all()
    
    if not memberships:
        raise HTTPException(status_code=404, detail="User task list not found (no workspace membership)")
        
    membership = memberships[0]
    
    task_workspace = session.get(Workspace, membership.workspace_gid)

    return {
        "data": {
            "gid": membership.gid,
            "resource_type": "user_task_list",
            "name": f"My tasks in {task_workspace.name}",
            "owner": {
                "gid": user.gid,
                "resource_type": "user",
                "name": user.name
            },
            "workspace": {
                "gid": task_workspace.gid,
                "resource_type": "workspace",
                "name": task_workspace.name
            }
        }
    }

