from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from app.database import get_session
from app.db_models import WorkspaceMembership, User, Workspace, Task
from app.models.schemas import *

router = APIRouter(tags=['Workspace memberships'])


@router.get("/workspace_memberships/{workspace_membership_gid}", response_model=dict | None, summary="Get a workspace membership")
async def getworkspacemembership(
    workspace_membership_gid: str,
    request: Request,
    session: Session = Depends(get_session)
):
    workspaceMembership = session.get(WorkspaceMembership, workspace_membership_gid)
    if not workspaceMembership:
        raise HTTPException(status_code=404, detail="Workspace membership not found")
        
    user = session.get(User, workspaceMembership.user_gid)
    workspace = session.get(Workspace, workspaceMembership.workspace_gid)
    
    if not user or not workspace:
         raise HTTPException(status_code=404, detail="Related user or workspace not found")

    return {
        "data": {
            "gid": workspaceMembership.gid,
            "resource_type": "workspace_membership",
            "user": {
                "gid": user.gid,
                "resource_type": "user",
                "name": user.name
            },
            "workspace": {
                "gid": workspace.gid,
                "resource_type": "workspace",
                "name": workspace.name
            },
            "user_task_list": {
                "gid": "12345", # Placeholder or fetched if exists
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
            },
            "is_active": workspaceMembership.is_active,
            "is_admin": workspaceMembership.is_admin,
            "is_guest": workspaceMembership.is_guest,
            "is_view_only": False, # Defaulting as not in DB
            "vacation_dates": {
                "start_on": None,
                "end_on": None
            },
            "created_at": workspaceMembership.created_at.isoformat() if workspaceMembership.created_at else None
        }
    }


@router.get("/users/{user_gid}/workspace_memberships", response_model=dict | None, summary="Get workspace memberships for a user")
async def getworkspacemembershipsforuser(
    user_gid: str,
    request: Request,
    session: Session = Depends(get_session)
):
    # Verify user exists?
    user = session.get(User, user_gid)
    if not user:
         raise HTTPException(status_code=404, detail="User not found")

    statement = select(WorkspaceMembership).where(WorkspaceMembership.user_gid == user_gid)
    workspaceMemberships = session.exec(statement).all()
    
    data = []
    for wm in workspaceMemberships:
        w_user = session.get(User, wm.user_gid)
        w_space = session.get(Workspace, wm.workspace_gid)
        if w_user and w_space:
            data.append({
                "gid": wm.gid,
                "resource_type": "workspace_membership",
                "user": {
                    "gid": w_user.gid,
                    "resource_type": "user",
                    "name": w_user.name
                },
                "workspace": {
                    "gid": w_space.gid,
                    "resource_type": "workspace",
                    "name": w_space.name
                }
            })

    return {
        "data": data,
        "next_page": None # Pagination not implemented yet
    }


@router.get("/workspaces/{workspace_gid}/workspace_memberships", response_model=dict | None, summary="Get the workspace memberships for a workspace")
async def getworkspacemembershipsforworkspace(
    workspace_gid: str,
    request: Request,
    session: Session = Depends(get_session)
):
    # Verify workspace exists
    workspace = session.get(Workspace, workspace_gid)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    statement = select(WorkspaceMembership).where(WorkspaceMembership.workspace_gid == workspace_gid)
    workspaceMemberships = session.exec(statement).all()
    
    data = []
    for wm in workspaceMemberships:
        w_user = session.get(User, wm.user_gid) # In this case user is variable
        w_space = workspace # All are in this workspace
        if w_user:
            data.append({
                "gid": wm.gid,
                "resource_type": "workspace_membership",
                "user": {
                    "gid": w_user.gid,
                    "resource_type": "user",
                    "name": w_user.name
                },
                "workspace": {
                    "gid": w_space.gid,
                    "resource_type": "workspace",
                    "name": w_space.name
                }
            })

    return {
        "data": data,
        "next_page": None
    }

