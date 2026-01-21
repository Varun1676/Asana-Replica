from fastapi import APIRouter, Request, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from app.database import get_session
from app.db_models import WorkspaceMembership, User, Project, Workspace
from app.models.schemas import *

router = APIRouter(tags=['Memberships'])


@router.get("/memberships", response_model=dict | None, summary="Get multiple memberships")
async def getmemberships(
    request: Request,
    parent: Optional[str] = None,
    member: Optional[str] = None,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    results = []
    
    # 1. Project Filter (Synthesize Project Memberships from Workspace Memberships)
    if parent:
        project = session.get(Project, parent)
        if project:
            # Find all users in the workspace of this project
            w_memberships = session.exec(select(WorkspaceMembership).where(WorkspaceMembership.workspace_gid == project.workspace_gid).limit(limit)).all()
            for wm in w_memberships:
                user = session.get(User, wm.user_gid)
                if user:
                    results.append({
                        "gid": wm.gid, # Use actual WM GID to allow deletion/retrieval? Or Synthetic? Using WM GID allows direct manipulation.
                        "resource_type": "membership",
                        "resource_subtype": "project_membership", # Pretending for API contract 
                        "parent": {
                            "gid": project.gid,
                            "resource_type": "project",
                            "name": project.name
                        },
                        "member": {
                            "gid": user.gid,
                            "resource_type": "user",
                            "name": user.name
                        },
                        "access_level": "editor" if wm.is_admin else "viewer"
                    })
    
    # 2. Member Filter
    elif member:
        # Get all workspace memberships for this user
        w_memberships = session.exec(select(WorkspaceMembership).where(WorkspaceMembership.user_gid == member).limit(limit)).all()
        for wm in w_memberships:
            ws = session.get(Workspace, wm.workspace_gid)
            if ws:
                 results.append({
                    "gid": wm.gid,
                    "resource_type": "membership",
                    "resource_subtype": "workspace_membership",
                    "parent": {
                        "gid": ws.gid,
                        "resource_type": "workspace",
                        "name": ws.name
                    },
                    "member": {
                        "gid": member,
                        "resource_type": "user"
                    },
                    "access_level": "admin" if wm.is_admin else "member"
                })

    return {"data": results}

@router.delete("/memberships/{membership_gid}", response_model=dict | None, summary="Delete a membership")
async def deletemembership(membership_gid: str, request: Request, session: Session = Depends(get_session)):
    # Try deleting WorkspaceMembership
    wm = session.get(WorkspaceMembership, membership_gid)
    if not wm:
        raise HTTPException(status_code=404, detail="Membership not found")
        
    session.delete(wm)
    session.commit()
    return {"data": {}}

@router.get("/memberships/{membership_gid}", response_model=dict | None, summary="Get a membership")
async def getmembership(membership_gid: str, request: Request, session: Session = Depends(get_session)):
    wm = session.get(WorkspaceMembership, membership_gid)
    if not wm:
         raise HTTPException(status_code=404, detail="Membership not found")
         
    user = session.get(User, wm.user_gid)
    ws = session.get(Workspace, wm.workspace_gid)
    
    return {
      "data": {
        "gid": wm.gid,
        "resource_type": "membership",
        "resource_subtype": "workspace_membership",
        "member": {
          "gid": user.gid if user else "",
          "resource_type": "user",
          "name": user.name if user else ""
        },
        "parent": {
          "gid": ws.gid if ws else "",
          "resource_type": "workspace",
          "name": ws.name if ws else ""
        },
        "access_level": "admin" if wm.is_admin else "member"
      }
    }

